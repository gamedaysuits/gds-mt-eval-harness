#!/usr/bin/env bash
# push_harness_mirror.sh — publish a CLEAN, SELF-CONTAINED snapshot of arena/
# to the public harness mirror (gamedaysuits/gds-mt-eval-harness) as a SINGLE
# ORPHAN COMMIT, force-pushed. The public repo is therefore always exactly one
# clean tree — it carries ZERO history.
#
# WHY ORPHAN + FORCE (not append, not `git subtree push`):
#   The monorepo's past commits contain data we may NOT redistribute — the
#   Wolvengrey lemma file (added 6c8eb7a3, removed 18acc2c4) and EdTeKLA
#   fixtures. The previous "append one snapshot commit" approach left those
#   blobs reachable in the mirror's early history (a live leak). A single
#   orphan commit force-pushed each time means no prior blob can ever survive.
#
# WHAT IS EXCLUDED FROM PUBLIC (IP / licensing — founder directive 2026-06-15):
#   - anything Wolvengrey / lemma-named (permission pending; never redistribute)
#   - EdTeKLA (CC BY-NC-SA, non-commercial): the edtekla adapter + its tests are
#     dropped, and the 3 edtekla datasets are stripped from the published
#     registry, so the public harness neither ships nor advertises EdTeKLA.
#   These stay in the PRIVATE monorepo (where the crk flagship eval runs) — they
#   are simply never published. NO synthetic stand-ins are created.
#
# Usage:
#   arena/scripts/push_harness_mirror.sh          # dry run: build + verify, no push
#   arena/scripts/push_harness_mirror.sh --push   # force-push the clean orphan commit
#
# Respects the monorepo rule: NO push without the founder's go-ahead (--push).

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

git remote get-url harness >/dev/null 2>&1 || {
  echo "error: remote 'harness' is not configured (git remote -v)" >&2; exit 1; }

# Only committed tracked state matters — the snapshot is built from HEAD:arena,
# so untracked run artifacts (arena/eval/logs/harness/*_report.json) are
# irrelevant and must not block a publish.
if [[ -n "$(git status --porcelain --untracked-files=no -- arena)" ]]; then
  echo "error: arena/ has uncommitted tracked changes — commit first so the" >&2
  echo "       snapshot is traceable to a monorepo commit." >&2
  exit 1
fi

MONOREPO_SHA="$(git rev-parse --short HEAD)"
MIRROR_URL="$(git remote get-url harness)"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# Tracked files only (git archive excludes .venv / build/ / .cache / __pycache__
# / *.pyc — they are untracked/gitignored, so they never reach the public repo).
git archive "HEAD:arena" | tar -x -C "$STAGE"

# --- exclude private-only content (IP) -------------------------------------
find "$STAGE" -iname '*edtekla*'   -print -delete
find "$STAGE" -iname '*lemmas*'    -print -delete
find "$STAGE" -iname '*wolvengrey*' -print -delete

# Strip the EdTeKLA datasets from the published registry so the public harness
# does not advertise a corpus it can't (and shouldn't) build.
if [[ -f "$STAGE/datasets/registry.json" ]]; then
  python3 - "$STAGE/datasets/registry.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
ds = d.get("datasets", [])
kept = [x for x in ds if "edtekla" not in json.dumps(x).lower()]
d["datasets"] = kept
json.dump(d, open(p, "w"), indent=2)
print(f"  registry: dropped {len(ds) - len(kept)} edtekla dataset(s), {len(kept)} remain")
PY
fi

# --- hard safety gate: forbidden DATA FILES must not remain -----------------
# The IP risk is the DATA itself — a file named lemmas.json (Wolvengrey) or any
# wolvengrey/edtekla-named file. Mere mentions in code/docs (the validator that
# loads a local lemmas.json at runtime, docs that CITE Wolvengrey/EdTeKLA as
# sources) are attribution/scholarship, not redistribution, and are fine.
if find "$STAGE" \( -iname 'lemmas.json' -o -iname '*wolvengrey*' -o -iname '*edtekla*' \) 2>/dev/null | grep -q .; then
  echo "error: a forbidden DATA FILE is present in the snapshot — aborting." >&2
  find "$STAGE" \( -iname 'lemmas.json' -o -iname '*wolvengrey*' -o -iname '*edtekla*' \) 2>/dev/null | sed "s#$STAGE/#    #"
  exit 1
fi

# Residual string MENTIONS (docs/code that name the sources but ship no data) —
# reported as a count, not fatal. Shared harness code keeps a lazily-imported
# edtekla builder stub (inert publicly: adapter + registry entries are gone),
# and the public docs cite EdTeKLA/Wolvengrey as sources of the Cree flagship.
RESID="$(grep -rilE 'edtekla|wolvengrey' "$STAGE" 2>/dev/null | wc -l | tr -d ' ')"
if [[ "${RESID:-0}" -gt 0 ]]; then
  echo "note: ${RESID} published file(s) MENTION EdTeKLA/Wolvengrey by name —"
  echo "      docs/code that cite the sources (attribution/scholarship), no data."
fi

FILE_COUNT="$(find "$STAGE" -type f | wc -l | tr -d ' ')"

# --- build a single orphan commit ------------------------------------------
cd "$STAGE"
git init -q
git checkout -q -b main
git add -A
git -c user.name="champollion-mirror" -c user.email="noreply@champollion.dev" \
  commit -q -m "harness: clean public snapshot from monorepo @${MONOREPO_SHA}

Single orphan commit (no history). EdTeKLA (CC BY-NC-SA) and Wolvengrey data
are excluded — published source only. See arena/scripts/push_harness_mirror.sh."
SNAP_SHA="$(git rev-parse --short HEAD)"
echo "Clean snapshot built: commit $SNAP_SHA, $FILE_COUNT files, orphan (no history)."

if [[ "${1:-}" == "--push" ]]; then
  git push --force "$MIRROR_URL" main
  echo "Force-pushed clean orphan snapshot to the public mirror (main)."
else
  echo
  echo "DRY RUN — nothing pushed. Re-run with --push to publish (founder go-ahead)."
fi
