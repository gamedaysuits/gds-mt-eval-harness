"""
Mesh wave builder — register fetch-from-source corpora for the highest
chaining-value language pairs.

The mission ("every language into every language by measured individual
pair chains") needs benchmark corpora for pairs BETWEEN already-covered
languages, not just more English-source spokes. This tool:

    1. Probes the pinned Tatoeba Challenge release via its index
       (``probe_tatoeba.mesh_report``) for candidate edges between
       languages already in the registry, ranked by chaining gain
       (global-efficiency delta on the benchmark graph).
    2. Builds each candidate deterministically from the consolidated
       test archive (``adapters.tatoeba_challenge_adapter``) into the
       gitignored cache — corpora are NEVER committed or rehosted.
    3. Registers each built corpus as ``access: "fetch-from-source"``,
       pinning the export URL, archive sha256, extraction recipe, and
       the built file's sha256 so any later rebuild (harness
       fetch-on-miss, community contributor, CI) is verified
       byte-identical.

Corpora whose built size lands below the 50-entry development floor
(fair scoring policy §5) are skipped and reported, not registered.

Usage (from arena/scripts/corpora-builder):
    python -m corpora_builder.build_mesh_wave \\
        --registry ../../datasets/registry.json \\
        --language-cards-dir ../../../cli/shared/language-cards \\
        [--limit 40] [--dry-run] [--yes]

Re-running is idempotent: existing registry ids are updated in place,
and pairs that already have a corpus (either direction) are never
candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

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
from corpora_builder.build_dev_corpora import _update_registry
from corpora_builder.probe_tatoeba import (
    FLOOR_N,
    fetch_release_index,
    mesh_report,
    parse_release_index,
)


def _taxonomy_notes_by_lang(datasets: list[dict]) -> dict[str, str]:
    """Existing taxonomy_note text per language code, from the registry.

    Macrolanguage caveats (que, mon, uzb, sqi, …) already recorded on
    existing corpora apply to any new corpus touching the same code —
    derive them from the registry rather than hardcoding a list.
    """
    notes: dict[str, str] = {}
    for ds in datasets:
        note = ds.get("taxonomy_note")
        lp = ds.get("language_pair")
        if not note or not lp:
            continue
        for lang in (lp["source"], lp["target"]):
            # A note names the code it caveats; attach only to that code.
            if f" {lang}" in note or f"code {lang}" in note:
                notes.setdefault(lang, note)
    return notes


def _registry_entry(
    candidate: dict,
    built_path: Path,
    built_size: int,
    rank: int,
    taxonomy_notes: dict[str, str],
    recipe: dict,
) -> dict:
    src, tgt = candidate["source"], candidate["target"]
    # The tar member uses the release's own code spelling (deu-zho, not
    # cmn-deu) — pin the member path as it exists in the archive.
    pair_key = release_pair_key(src, tgt)
    sha256 = hashlib.sha256(built_path.read_bytes()).hexdigest()

    entry = {
        "id": f"tatoeba-{src}-{tgt}-dev",
        "name": f"Tatoeba {src}→{tgt} Development Corpus",
        "version": str(DEFAULT_RECIPE["builder_version"]),
        "language_pair": {"source": src, "target": tgt},
        "size": built_size,
        "domain": "mixed",
        "domain_distribution": domain_distribution(built_path),
        "url": None,
        "sha256": sha256,
        "access": "fetch-from-source",
        "do_not_train": True,
        "license": "CC-BY-2.0",
        "source": "Tatoeba (https://tatoeba.org)",
        "path": f"curated/{src}-{tgt}-dev-v1.json",
        "segment": "development",
        "notes": (
            f"Mesh wave 1 (2026-06-12), chaining rank #{rank} "
            f"(gain {candidate['chaining_gain']:.6f}"
            f"{', family bridge' if candidate.get('bridges_families') else ''}). "
            f"NOT hosted in git — the harness rebuilds it on demand from "
            f"the pinned Tatoeba Challenge consolidated test archive into "
            f"arena/datasets/.cache/ (see source_export)."
        ),
        "attribution": (
            "Tatoeba (CC-BY-2.0), via Tatoeba Challenge 2023-09-26"
        ),
        "source_export": {
            "builder": "tatoeba-challenge",
            "url": TEST_TAR_URL,
            "sha256": TEST_TAR_SHA256,
            "member": f"data/test-{RELEASE}/{pair_key}/test.txt",
            "index_url": INDEX_URL,
            "license": "CC-BY-2.0",
            "license_url": "https://creativecommons.org/licenses/by/2.0/",
            "recipe": dict(recipe),
        },
    }
    note = taxonomy_notes.get(tgt) or taxonomy_notes.get(src)
    if note:
        entry["taxonomy_note"] = note
    return entry


def build_wave(
    registry_path: Path,
    cards_dir: Path,
    cache_dir: Path,
    *,
    limit: int | None = None,
    min_tier: str = "floor",
    dry_run: bool = False,
    auto_yes: bool = False,
    survival: float | None = None,
) -> dict:
    """Probe, build, and register one mesh wave. Returns a summary dict."""
    from corpora_builder.adapters.tatoeba_challenge_adapter import (
        build_corpus_file,
    )

    tar_path = ensure_test_tar(cache_dir, auto_yes=auto_yes)
    available = {iso_pair_key(p) for p in list_tar_pairs(tar_path)}
    index = parse_release_index(fetch_release_index(cache_dir))

    report = mesh_report(
        registry_path, cards_dir, index,
        available_pairs=available, survival=survival,
    )
    tiers_ok = (
        {"preferred"} if min_tier == "preferred" else {"preferred", "floor"}
    )
    candidates = [c for c in report["candidates"] if c["tier"] in tiers_ok]
    if limit is not None:
        candidates = candidates[:limit]

    print(f"  Wave plan: {len(candidates)} candidates "
          f"(of {len(report['candidates'])} viable; min tier: {min_tier})")
    if dry_run:
        for i, c in enumerate(candidates, 1):
            print(f"    #{i:<3} {c['direction']:<12} "
                  f"gain={c['chaining_gain']:.6f} test={c['test_size']}")
        return {"planned": candidates, "built": [], "skipped": [],
                "report": report}

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    taxonomy_notes = _taxonomy_notes_by_lang(registry.get("datasets", []))

    built_entries: list[dict] = []
    skipped: list[dict] = []
    for i, cand in enumerate(candidates, 1):
        src, tgt = cand["source"], cand["target"]
        dest = cache_dir.parent / "curated" / f"{src}-{tgt}-dev-v1.json"
        label = f"[{i}/{len(candidates)}] {src}>{tgt}"

        def _attempt(recipe: dict) -> tuple[Path | None, int]:
            try:
                built = build_corpus_file(
                    dest,
                    source_lang=src,
                    target_lang=tgt,
                    cache_dir=cache_dir,
                    recipe=recipe,
                    auto_yes=True,  # batch license confirmed via ensure_test_tar
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
            built, size = _attempt(recipe)
            if size < FLOOR_N:
                # Word windows starve source languages without whitespace
                # word boundaries (jpn, cmn, tha, …) — nearly every
                # sentence is one "word". Retry with the character window
                # and keep it if it clears the floor; the registry pins
                # whichever recipe produced the registered corpus.
                chars_recipe = {**recipe, "length_unit": "chars"}
                chars_built, chars_size = _attempt(chars_recipe)
                if chars_size > size:
                    built, size, recipe = chars_built, chars_size, chars_recipe
        except Exception as exc:  # noqa: BLE001 — per-pair isolation
            print(f"    {label}: BUILD FAILED — {exc}")
            skipped.append({**cand, "reason": f"build failed: {exc}"})
            continue

        if size < FLOOR_N or built is None:
            print(f"    {label}: {size} entries < {FLOOR_N}-entry floor — "
                  f"not registered (fair scoring policy §5)")
            skipped.append({**cand, "built_size": size,
                            "reason": f"below {FLOOR_N}-entry floor"})
            continue

        entry = _registry_entry(cand, built, size, i, taxonomy_notes, recipe)
        built_entries.append(entry)
        bridge = " [family bridge]" if cand.get("bridges_families") else ""
        unit = " (char window)" if recipe["length_unit"] == "chars" else ""
        print(f"    {label}: {size} entries, "
              f"gain {cand['chaining_gain']:.6f}{bridge}{unit}")

    if built_entries:
        _update_registry(registry_path, built_entries)

    return {
        "planned": candidates,
        "built": built_entries,
        "skipped": skipped,
        "report": report,
    }


def repin_wave(
    registry_path: Path,
    cache_dir: Path,
    *,
    auto_yes: bool = False,
) -> dict:
    """Rebuild every tatoeba-challenge corpus and re-pin drifted hashes.

    Maintenance pass for when build code changes behaviour (enrichment
    heuristics, provenance shape, orientation fixes): rebuilds each
    registered corpus fresh from its pinned recipe, then updates
    ``sha256``/``size``/``domain_distribution`` and records the full
    effective recipe. Entries whose rebuild matches the pin are left
    untouched. Never deletes or renames entries.
    """
    from corpora_builder.adapters.tatoeba_challenge_adapter import (
        build_corpus_file,
    )

    ensure_test_tar(cache_dir, auto_yes=auto_yes)
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    updated: list[dict] = []
    unchanged = 0
    for entry in registry.get("datasets", []):
        export = entry.get("source_export") or {}
        if export.get("builder") != "tatoeba-challenge":
            continue
        src = entry["language_pair"]["source"]
        tgt = entry["language_pair"]["target"]
        dest = cache_dir.parent / Path(entry["path"])
        dest.unlink(missing_ok=True)  # force a from-source rebuild
        effective = {**DEFAULT_RECIPE, **(export.get("recipe") or {})}
        built = build_corpus_file(
            dest,
            source_lang=src,
            target_lang=tgt,
            cache_dir=cache_dir,
            recipe=effective,
            tar_url=export.get("url", TEST_TAR_URL),
            tar_sha256=export.get("sha256", TEST_TAR_SHA256),
            auto_yes=True,
        )
        sha = hashlib.sha256(built.read_bytes()).hexdigest()
        size = json.loads(built.read_text(encoding="utf-8"))["entry_count"]
        if sha == entry.get("sha256") and size == entry.get("size") \
                and export.get("recipe") == effective:
            unchanged += 1
            continue
        entry["sha256"] = sha
        entry["size"] = size
        entry["domain_distribution"] = domain_distribution(built)
        export["recipe"] = effective
        updated.append(entry)
        print(f"    re-pinned {entry['id']}: size {size}, sha {sha[:12]}…")

    if updated:
        _update_registry(registry_path, updated)
    print(f"  Re-pin complete: {len(updated)} updated, {unchanged} unchanged")
    return {"updated": [e["id"] for e in updated], "unchanged": unchanged}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--language-cards-dir", required=True)
    ap.add_argument(
        "--cache-dir",
        default=None,
        help="Cache for the consolidated archive (default: "
             "<registry dir>/.cache/tatoeba-challenge).",
    )
    ap.add_argument("--limit", type=int, default=None,
                    help="Build only the top N candidates by chaining gain.")
    ap.add_argument("--min-tier", choices=("floor", "preferred"),
                    default="floor")
    ap.add_argument("--survival", type=float, default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="Rank and print the wave plan without building.")
    ap.add_argument("--yes", "-y", action="store_true",
                    help="Skip the license confirmation prompt.")
    ap.add_argument("--report-output", default=None,
                    help="Write the full wave summary JSON here.")
    ap.add_argument("--repin", action="store_true",
                    help="Maintenance: rebuild every registered "
                         "tatoeba-challenge corpus and re-pin drifted "
                         "sha256/size/recipe values instead of building "
                         "new pairs.")
    args = ap.parse_args()

    registry_path = Path(args.registry).resolve()
    cache_dir = (
        Path(args.cache_dir).resolve()
        if args.cache_dir
        else registry_path.parent / ".cache" / "tatoeba-challenge"
    )

    if args.repin:
        repin_wave(registry_path, cache_dir, auto_yes=args.yes)
        return 0

    summary = build_wave(
        registry_path,
        Path(args.language_cards_dir).resolve(),
        cache_dir,
        limit=args.limit,
        min_tier=args.min_tier,
        dry_run=args.dry_run,
        auto_yes=args.yes,
        survival=args.survival,
    )

    print(f"\n  Built+registered: {len(summary['built'])}; "
          f"skipped: {len(summary['skipped'])}")
    if args.report_output:
        out = Path(args.report_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        print(f"  Wave summary written to: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
