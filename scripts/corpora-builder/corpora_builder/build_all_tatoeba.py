"""
Build all Tatoeba cards — generate eval corpora CARDS for every viable
Tatoeba Challenge pair whose estimated usable entries meet the 100-entry
floor (FLOOR_N).

Unlike ``build_mesh_wave`` (which registers entries in the arena's
registry.json), this script produces self-contained **corpora card**
JSON files in ``cli/shared/corpora-cards/`` — the authoritative metadata
format consumed by the CLI and the web UI.

The build pipeline is identical to mesh wave: consolidated test tar →
word-count filter (char-window fallback for CJK) → domain/difficulty/
register enrichment → seeded stratified sampling → deterministic corpus
JSON. Each resulting card follows the exact format of existing eval
cards (see ``eval-cmn-jpn-tatoeba-dev-v1.json``).

Re-running is idempotent: pairs whose card file already exists in the
output directory are skipped.

Usage (from arena/scripts/corpora-builder):
    python -m corpora_builder.build_all_tatoeba \\
        [--limit 10] [--dry-run] [--yes]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from corpora_builder.adapters.tatoeba_challenge_adapter import (
    DEFAULT_RECIPE,
    INDEX_URL,
    RELEASE,
    TEST_TAR_SHA256,
    TEST_TAR_URL,
    domain_distribution,
    ensure_test_tar,
    iso_pair_key,
    list_tar_pairs,
    release_pair_key,
)
from corpora_builder.probe_tatoeba import (
    DEFAULT_SURVIVAL,
    FLOOR_N,
    PREFERRED_N,
    calibrate_survival,
    fetch_release_index,
    parse_release_index,
)


# ---------------------------------------------------------------------------
# Paths — resolved relative to the repo root (three levels up from this
# script: corpora_builder → corpora-builder → scripts → arena).
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    """Walk up from this file to the repository root."""
    # this file:  arena/scripts/corpora-builder/corpora_builder/build_all_tatoeba.py
    # repo root:  ../../../../
    return Path(__file__).resolve().parent.parent.parent.parent.parent


def _default_cards_dir() -> Path:
    return _repo_root() / "cli" / "shared" / "corpora-cards"


def _default_cache_dir() -> Path:
    return _repo_root() / "arena" / "datasets" / ".cache" / "tatoeba-challenge"


def _default_curated_dir() -> Path:
    return _repo_root() / "arena" / "datasets" / "curated"


def _default_registry_path() -> Path:
    return _repo_root() / "arena" / "datasets" / "registry.json"


# ---------------------------------------------------------------------------
# Contamination risk heuristic — mirrors logic already used in existing
# cards. "HIGH" if the raw test split is huge (≥10 000); "MEDIUM" if the
# pair has ≥100 usable entries (the vast majority of Tatoeba); "LOW" for
# pairs right at the floor with limited web presence.
# ---------------------------------------------------------------------------

def _contamination_risk(test_size: int) -> str:
    """Heuristic risk tier based on raw test-split size."""
    if test_size >= 10_000:
        return "HIGH"
    if test_size >= 500:
        return "MEDIUM"
    return "LOW"


def _contamination_reasoning(
    src: str, tgt: str, size: int, test_size: int, risk: str,
) -> str:
    """Human-readable contamination note matching existing card style."""
    return (
        f"Tatoeba {src}→{tgt} is a "
        f"{'high' if test_size >= 5000 else 'moderate' if test_size >= 500 else 'low'}"
        f"-resource pair with {size} entries. "
        f"{'Both languages are well-represented in web crawl data. ' if risk != 'LOW' else ''}"
        f"Individual sentences may appear in frontier LLM training data "
        f"via broad tatoeba.org crawls."
    )


# ---------------------------------------------------------------------------
# Domain distribution → fractional form used in cards
# ---------------------------------------------------------------------------

def _domain_distribution_fractions(
    raw_counts: dict[str, int],
    total: int,
) -> dict[str, float]:
    """Convert per-domain counts to rounded fractions (sum ≈ 1.0).

    Existing cards use fractional distributions (0.69, 0.035, …); the
    adapter's ``domain_distribution`` returns raw counts.  Round to
    three decimal places to keep the card readable.
    """
    if total == 0:
        return {}
    return {
        domain: round(count / total, 3)
        for domain, count in sorted(raw_counts.items())
    }


# ---------------------------------------------------------------------------
# Card builder
# ---------------------------------------------------------------------------

def _build_card(
    src: str,
    tgt: str,
    *,
    built_path: Path,
    size: int,
    recipe: dict[str, Any],
    test_size: int,
) -> dict:
    """Assemble a corpora card dict matching the existing eval card format.

    The output schema matches ``eval-cmn-jpn-tatoeba-dev-v1.json``
    exactly — every field present in that exemplar is reproduced here.
    """
    pair_key = release_pair_key(src, tgt)
    sha256 = hashlib.sha256(built_path.read_bytes()).hexdigest()

    raw_dist = domain_distribution(built_path)
    frac_dist = _domain_distribution_fractions(raw_dist, size)
    # Determine the domain label: "mixed" when multiple domains, else the single domain
    domain_label = "mixed" if len(frac_dist) > 1 else next(iter(frac_dist), "mixed")

    risk = _contamination_risk(test_size)

    card: dict[str, Any] = {
        "id": f"eval-{src}-{tgt}-tatoeba-dev-v1",
        "type": "eval",
        "name": f"Tatoeba {src}→{tgt} Development Corpus",
        "version": str(DEFAULT_RECIPE["builder_version"]),
        "pair": {
            "source": src,
            "target": tgt,
            "direction": "unidirectional",
        },
        "description": (
            f"Mesh wave dev corpus built from Tatoeba Challenge "
            f"{RELEASE}. {size} entries, stratified across "
            f"{len(frac_dist)} domain(s). NOT hosted in git — rebuilt "
            f"deterministically on demand from the pinned upstream "
            f"Tatoeba Challenge archive."
        ),
        "source": {
            "publisher": "Tatoeba community (https://tatoeba.org)",
            "url": "https://tatoeba.org",
            "paper": "https://arxiv.org/abs/2010.06354",
            "citation": (
                "Tiedemann (2020). The Tatoeba Translation Challenge "
                "— Realistic Data Sets for Low Resource and "
                "Multilingual MT."
            ),
            "fundedBy": None,
            "repo_url": TEST_TAR_URL,
            "builder": "tatoeba-challenge",
            "sha256": sha256,
            "license": "CC-BY-2.0",
            "license_url": "https://creativecommons.org/licenses/by/2.0/",
            "member": f"data/test-{RELEASE}/{pair_key}/test.txt",
            "recipe": {
                "release": str(recipe["release"]),
                "split": str(recipe["split"]),
                "seed": int(recipe["seed"]),
                "max_entries": int(recipe["max_entries"]),
                "length_unit": str(recipe["length_unit"]),
                "min_words": int(recipe["min_words"]),
                "max_words": int(recipe["max_words"]),
                "min_chars": int(recipe["min_chars"]),
                "max_chars": int(recipe["max_chars"]),
                "variety_filter": recipe.get("variety_filter"),
                "created": str(recipe["created"]),
                "builder_version": str(recipe["builder_version"]),
            },
        },
        "license": {
            "spdx": "CC-BY-2.0",
            "commercial": True,
            "redistribution": True,
            "aiTraining": None,
            "notes": None,
        },
        "dev": {
            "size": size,
            "sizeUnit": "entries",
            "domain": domain_label,
            "domainDistribution": frac_dist,
            "dataFile": f"curated/{src}-{tgt}-dev-v1.json",
            "format": "harness-json",
        },
        "secretTest": None,
        "stewardship": None,
        "submission": None,
        "quality": {
            "humanTranslated": True,
            "translatorQualifications": None,
            "reviewProcess": None,
            "orthography": None,
        },
        "contamination": {
            "risk": risk,
            "reasoning": _contamination_reasoning(
                src, tgt, size, test_size, risk,
            ),
        },
        "doNotTrain": True,
        "_provenance": {
            "addedAt": str(date.today()),
            "lastUpdated": None,
            "populatedFrom": (
                f"Generated by build_all_tatoeba from Tatoeba Challenge "
                f"{RELEASE} consolidated test archive. "
                f"Size and domain distribution verified against curated "
                f"data file. License from Tatoeba Challenge terms "
                f"(CC-BY-2.0). Fetch-from-source build recipe pinned in "
                f"source block."
            ),
        },
    }
    return card


# ---------------------------------------------------------------------------
# Main build loop
# ---------------------------------------------------------------------------

def _existing_card_pairs(cards_dir: Path) -> set[str]:
    """Return the set of ``src-tgt`` pair keys that already have cards.

    Parses filenames matching ``eval-{src}-{tgt}-tatoeba-dev-v1.json``.
    """
    pairs: set[str] = set()
    if not cards_dir.is_dir():
        return pairs
    for f in cards_dir.glob("eval-*-*-tatoeba-dev-v1.json"):
        # Filename: eval-{src}-{tgt}-tatoeba-dev-v1.json
        # We need to extract src and tgt from the stem
        stem = f.stem  # e.g. "eval-cmn-jpn-tatoeba-dev-v1"
        parts = stem.split("-")
        # parts: ["eval", src, tgt, "tatoeba", "dev", "v1"]
        if len(parts) >= 6 and parts[0] == "eval" and parts[3] == "tatoeba":
            src, tgt = parts[1], parts[2]
            pairs.add(f"{src}-{tgt}")
    return pairs


def build_all(
    cards_dir: Path,
    cache_dir: Path,
    curated_dir: Path,
    *,
    limit: int | None = None,
    dry_run: bool = False,
    auto_yes: bool = False,
) -> dict:
    """Probe, build, and write eval cards for all viable Tatoeba pairs.

    Returns a summary dict with counts of built, skipped, and failed pairs.
    """
    from corpora_builder.adapters.tatoeba_challenge_adapter import (
        build_corpus_file,
    )

    # ── 1. Fetch release index and list available pairs in the tar ─────
    print("  Fetching Tatoeba release index…")
    index = parse_release_index(fetch_release_index(cache_dir))
    print(f"  Index contains {len(index)} pair entries.")

    print("  Ensuring consolidated test tar…")
    tar_path = ensure_test_tar(cache_dir, auto_yes=auto_yes)
    available = {iso_pair_key(p) for p in list_tar_pairs(tar_path)}
    print(f"  Test tar contains {len(available)} pairs.")

    # ── 2. Compute survival rate from any existing registry ────────────
    registry_path = _default_registry_path()
    survival = DEFAULT_SURVIVAL
    if registry_path.exists():
        try:
            registry = json.loads(
                registry_path.read_text(encoding="utf-8")
            )
            cal = calibrate_survival(
                registry.get("datasets", []), index,
            )
            if cal is not None:
                survival = cal
                print(f"  Calibrated survival rate: {survival:.4f}")
        except (OSError, json.JSONDecodeError):
            pass
    if survival == DEFAULT_SURVIVAL:
        print(f"  Using default survival rate: {survival}")

    # ── 3. Filter to viable pairs (est_usable >= FLOOR_N) ─────────────
    #    We iterate every pair key present in the test tar — not just
    #    "lit" languages from the registry — because this script aims to
    #    generate cards for ALL viable pairs, not only mesh edges.
    # Pre-compute language presence once for orientation decisions
    from corpora_builder.probe_tatoeba import language_presence
    presence = language_presence(index)

    viable_pairs: list[dict] = []
    for pair_key in sorted(available):
        row = index.get(pair_key)
        if not row or row["test_size"] <= 0:
            continue
        est_usable = int(row["test_size"] * survival)
        if est_usable < FLOOR_N:
            continue
        # Determine direction: higher-resource language as source
        a, b = pair_key.split("-", 1)
        if presence.get(a, 0) >= presence.get(b, 0):
            src, tgt = a, b
        else:
            src, tgt = b, a
        viable_pairs.append({
            "pair_key": pair_key,
            "source": src,
            "target": tgt,
            "test_size": row["test_size"],
            "est_usable": est_usable,
        })

    print(f"  Viable pairs (est ≥ {FLOOR_N}): {len(viable_pairs)}")

    # ── 4. Skip pairs that already have cards ─────────────────────────
    existing = _existing_card_pairs(cards_dir)
    candidates: list[dict] = []
    already_have = 0
    for vp in viable_pairs:
        card_key = f"{vp['source']}-{vp['target']}"
        if card_key in existing:
            already_have += 1
            continue
        candidates.append(vp)

    if limit is not None:
        candidates = candidates[:limit]

    print(f"  Candidates to build: {len(candidates)} "
          f"(skipping {already_have} with existing cards)")

    if dry_run:
        print("\n  DRY RUN — would build the following cards:\n")
        for i, c in enumerate(candidates, 1):
            print(f"    #{i:<3} {c['source']}→{c['target']}  "
                  f"test={c['test_size']}  est~{c['est_usable']}")
        return {
            "planned": len(candidates),
            "built": 0,
            "skipped_existing": already_have,
            "failed": 0,
            "dry_run": True,
        }

    # ── 5. Build each viable pair ─────────────────────────────────────
    built_count = 0
    failed: list[dict] = []
    skipped_floor: list[dict] = []

    for i, cand in enumerate(candidates, 1):
        src, tgt = cand["source"], cand["target"]
        dest = curated_dir / f"{src}-{tgt}-dev-v1.json"
        label = f"[{i}/{len(candidates)}] {src}→{tgt}"

        # Inner build attempt — mirrors build_mesh_wave's retry logic
        def _attempt(recipe: dict) -> tuple[Path | None, int]:
            try:
                built = build_corpus_file(
                    dest,
                    source_lang=src,
                    target_lang=tgt,
                    cache_dir=cache_dir,
                    recipe=recipe,
                    auto_yes=True,  # license already confirmed via ensure_test_tar
                )
            except ValueError as exc:
                if "window" not in str(exc):
                    raise
                return None, 0  # length filter rejected everything
            size = json.loads(
                built.read_text(encoding="utf-8")
            )["entry_count"]
            return built, size

        recipe = dict(DEFAULT_RECIPE)
        try:
            built_path, size = _attempt(recipe)

            # Word windows starve CJK languages (jpn, cmn, tha, …)
            # where every sentence is one "word". Retry with the char
            # window and keep whichever recipe yields more entries.
            if size < FLOOR_N:
                chars_recipe = {**recipe, "length_unit": "chars"}
                chars_built, chars_size = _attempt(chars_recipe)
                if chars_size > size:
                    built_path, size, recipe = (
                        chars_built, chars_size, chars_recipe,
                    )
        except Exception as exc:  # noqa: BLE001 — per-pair isolation
            print(f"    {label}: BUILD FAILED — {exc}")
            failed.append({"pair": f"{src}-{tgt}", "reason": str(exc)})
            continue

        if size < FLOOR_N or built_path is None:
            print(f"    {label}: {size} entries < {FLOOR_N}-entry floor — skipped")
            skipped_floor.append({"pair": f"{src}-{tgt}", "built_size": size})
            continue

        # ── 5c. Generate the corpora card ─────────────────────────────
        card = _build_card(
            src, tgt,
            built_path=built_path,
            size=size,
            recipe=recipe,
            test_size=cand["test_size"],
        )

        # ── 5d. Write the card ────────────────────────────────────────
        card_path = cards_dir / f"eval-{src}-{tgt}-tatoeba-dev-v1.json"
        cards_dir.mkdir(parents=True, exist_ok=True)
        card_path.write_text(
            json.dumps(card, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        unit = " (char window)" if recipe["length_unit"] == "chars" else ""
        print(f"    {label}: {size} entries{unit} → {card_path.name}")
        built_count += 1

    # ── 6. Report ─────────────────────────────────────────────────────
    print(f"\n  ═══ Summary ═══")
    print(f"  Built:          {built_count}")
    print(f"  Skipped (exist):{already_have}")
    print(f"  Skipped (floor):{len(skipped_floor)}")
    print(f"  Failed:         {len(failed)}")

    if failed:
        print("\n  Failed pairs:")
        for f_entry in failed:
            print(f"    {f_entry['pair']}: {f_entry['reason']}")

    return {
        "planned": len(candidates),
        "built": built_count,
        "skipped_existing": already_have,
        "skipped_floor": len(skipped_floor),
        "failed": len(failed),
        "failed_pairs": failed,
        "dry_run": False,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--cards-dir",
        default=None,
        help="Output directory for corpora card JSON files "
             "(default: cli/shared/corpora-cards).",
    )
    ap.add_argument(
        "--cache-dir",
        default=None,
        help="Cache for the consolidated archive "
             "(default: arena/datasets/.cache/tatoeba-challenge).",
    )
    ap.add_argument(
        "--curated-dir",
        default=None,
        help="Directory for built corpus data files "
             "(default: arena/datasets/curated).",
    )
    ap.add_argument(
        "--limit", type=int, default=None,
        help="Build only the first N candidates (useful for testing).",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="List candidates without building or writing any files.",
    )
    ap.add_argument(
        "--yes", "-y", action="store_true",
        help="Skip the license confirmation prompt.",
    )
    ap.add_argument(
        "--report-output", default=None,
        help="Write the build summary JSON to this path.",
    )
    args = ap.parse_args()

    cards_dir = (
        Path(args.cards_dir).resolve()
        if args.cards_dir
        else _default_cards_dir()
    )
    cache_dir = (
        Path(args.cache_dir).resolve()
        if args.cache_dir
        else _default_cache_dir()
    )
    curated_dir = (
        Path(args.curated_dir).resolve()
        if args.curated_dir
        else _default_curated_dir()
    )

    summary = build_all(
        cards_dir,
        cache_dir,
        curated_dir,
        limit=args.limit,
        dry_run=args.dry_run,
        auto_yes=args.yes,
    )

    if args.report_output:
        out = Path(args.report_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  Build summary written to: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
