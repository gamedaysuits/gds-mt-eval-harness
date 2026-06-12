#!/usr/bin/env bash
# push_harness_mirror.sh — publish a clean SNAPSHOT of arena/ to the public
# harness mirror (gamedaysuits/gds-mt-eval-harness).
#
# WHY NOT `git subtree push`: the monorepo's history contains the Wolvengrey
# lemma data in past commits (added 6c8eb7a3, removed 18acc2c4 — data we may
# not redistribute). A subtree split regenerates that history, so a plain
# subtree push would re-leak it into the public repo (and be rejected as
# non-fast-forward anyway, because the mirror's history was reset to a clean
# root after the 2026-06-12 leak response). Instead, this script publishes
# the CURRENT arena/ tree as one new commit on top of the mirror's existing
# clean history — no monorepo history travels.
#
# Usage:
#   arena/scripts/push_harness_mirror.sh          # dry run: build + show, no push
#   arena/scripts/push_harness_mirror.sh --push   # actually push (founder go-ahead)
#
# Requirements: run from anywhere inside the monorepo; remote `harness` must
# exist (git remote -v). Respects the monorepo rule: NO push without the
# founder's explicit go-ahead — hence the --push flag.

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if ! git remote get-url harness >/dev/null 2>&1; then
  echo "error: remote 'harness' is not configured (git remote -v)" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain -- arena)" ]]; then
  echo "error: arena/ has uncommitted changes — commit first so the snapshot" >&2
  echo "       is traceable to a monorepo commit." >&2
  exit 1
fi

MONOREPO_SHA="$(git rev-parse --short HEAD)"
BRANCH="main"

echo "Fetching mirror state…"
git fetch harness "$BRANCH"

# Tree of arena/ at HEAD (content only — no history).
ARENA_TREE="$(git rev-parse "HEAD:arena")"

# Safety: the snapshot tree must not contain known non-redistributable files.
if git ls-tree -r --name-only "$ARENA_TREE" | grep -qiE 'lemmas\.json|wolvengrey'; then
  echo "error: snapshot tree contains lemma/Wolvengrey-named files — aborting." >&2
  exit 1
fi

PARENT="$(git rev-parse "harness/$BRANCH")"

if [[ "$(git rev-parse "harness/$BRANCH^{tree}")" == "$ARENA_TREE" ]]; then
  echo "Mirror is already up to date with arena/ at $MONOREPO_SHA — nothing to push."
  exit 0
fi

COMMIT="$(git commit-tree "$ARENA_TREE" -p "$PARENT" \
  -m "sync: arena snapshot from monorepo @${MONOREPO_SHA}")"

echo "Built snapshot commit: $COMMIT"
echo "  parent (mirror):     $PARENT"
echo "  tree (arena@HEAD):   $ARENA_TREE"
git diff --stat "$PARENT" "$COMMIT" | tail -3

if [[ "${1:-}" == "--push" ]]; then
  git push harness "$COMMIT:refs/heads/$BRANCH"
  echo "Pushed to harness/$BRANCH."
else
  echo
  echo "DRY RUN — nothing pushed. To publish (founder go-ahead required):"
  echo "  git push harness $COMMIT:refs/heads/$BRANCH"
  echo "or rerun with --push."
fi
