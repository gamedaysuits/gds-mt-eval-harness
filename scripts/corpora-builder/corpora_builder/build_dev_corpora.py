"""
Batch corpus builder — builds development corpora for all viable Tatoeba pairs.

Usage:
    python -m corpora_builder.build_dev_corpora \\
        --language-cards-dir /path/to/language-cards \\
        --output-dir arena/datasets/curated \\
        --registry arena/datasets/registry.json

Workflow:
    1. Probe Tatoeba for all viable language pairs
    2. Show license info, ask for single y/n confirmation
    3. For each viable pair: download → parse → enrich → sample → write
    4. Update the corpus registry with all built corpora
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from corpora_builder import __version__
from corpora_builder.licensing import (
    LicenseInfo,
    TATOEBA_LICENSE,
    build_tatoeba_url,
    confirm_batch_download,
)
from corpora_builder.probe_tatoeba import (
    PairProbe,
    load_language_codes_from_cards,
    probe_all_pairs,
)


def _build_single_corpus(
    source_lang: str,
    target_lang: str,
    output_dir: Path,
    *,
    max_entries: int = 200,
    min_words: int = 3,
    max_words: int = 50,
    seed: int = 42,
) -> dict | None:
    """Build a single corpus for one language pair.

    Downloads from Tatoeba, enriches, samples, and writes corpus JSON.

    Returns:
        Registry entry dict for this corpus, or None if the pair
        yielded too few entries to be useful.
    """
    import random
    from collections import Counter

    from corpora_builder.adapters.tatoeba_adapter import TatoebaAdapter
    from corpora_builder.cli import _enrich_entry, _filter_by_word_count, _stratified_sample
    from corpora_builder.schema import Corpus

    # Minimum entries below which we skip this pair entirely.
    # A dev corpus with fewer than 30 entries isn't useful for
    # testing pipeline correctness or validating metric plugins.
    MIN_VIABLE_ENTRIES = 30

    adapter = TatoebaAdapter()
    rng = random.Random(seed)
    download_url = build_tatoeba_url(source_lang, target_lang)

    # Fetch (downloads + parses)
    try:
        raw_entries = adapter.fetch(
            source_lang=source_lang,
            target_lang=target_lang,
            download_url=download_url,
        )
    except Exception as exc:
        print(f"    ❌ Failed: {exc}")
        return None

    if len(raw_entries) < MIN_VIABLE_ENTRIES:
        print(
            f"    ⚠️  Only {len(raw_entries)} entries after parsing — "
            f"below minimum of {MIN_VIABLE_ENTRIES}, skipping."
        )
        return None

    # Filter by word count
    filtered = _filter_by_word_count(raw_entries, min_words, max_words)
    if len(filtered) < MIN_VIABLE_ENTRIES:
        print(
            f"    ⚠️  Only {len(filtered)} entries after word-count filter — "
            f"below minimum of {MIN_VIABLE_ENTRIES}, skipping."
        )
        return None

    # Enrich (domain + difficulty + register)
    enriched = []
    for raw in filtered:
        try:
            enriched.append(_enrich_entry(raw, adapter.name))
        except ValueError as exc:
            # _enrich_entry raises ValueError for domain/register issues
            # which should never happen with the classifier, but log if so
            print(f"    ⚠️  Enrichment error on entry {raw.source_id}: {exc}")
            continue

    if len(enriched) < MIN_VIABLE_ENTRIES:
        print(
            f"    ⚠️  Only {len(enriched)} entries after enrichment — "
            f"below minimum of {MIN_VIABLE_ENTRIES}, skipping."
        )
        return None

    # Stratified sampling
    sampled = _stratified_sample(enriched, max_entries, rng)

    # Build corpus object
    unique_domains = sorted(set(entry.domain for entry in sampled))
    now_utc = datetime.now(timezone.utc).isoformat()

    corpus_id = f"tatoeba-{source_lang}-{target_lang}-dev"
    corpus = Corpus(
        corpus_id=corpus_id,
        version=__version__,
        language_pair={
            "source": source_lang,
            "target": target_lang,
        },
        segment="development",
        created=now_utc,
        entry_count=len(sampled),
        domains=unique_domains,
        entries=sampled,
        provenance={
            "builder": "champollion-corpora-builder",
            "builder_version": __version__,
            "source_adapter": "tatoeba",
            "seed": seed,
            "min_words": min_words,
            "max_words": max_words,
            "license": "CC-BY-2.0",
            "source_url": "https://tatoeba.org",
        },
    )

    # Write output
    filename = f"{source_lang}-{target_lang}-dev-v1.json"
    output_path = output_dir / filename
    corpus.to_json(output_path)

    # Domain distribution for the registry
    domain_counts = dict(Counter(entry.domain for entry in sampled))

    return {
        "id": corpus_id,
        "name": f"Tatoeba {source_lang}→{target_lang} Development Corpus",
        "version": __version__,
        "language_pair": {"source": source_lang, "target": target_lang},
        "size": len(sampled),
        "domain": "mixed",
        "domain_distribution": domain_counts,
        "url": None,
        "sha256": None,  # computed post-build if needed
        "access": "local",
        "do_not_train": True,
        "license": "CC-BY-2.0",
        "source": "Tatoeba (https://tatoeba.org)",
        "path": str(output_path.relative_to(output_dir.parent)),
        "segment": "development",
        "notes": (
            f"Auto-built by corpora-builder v{__version__}. "
            f"{len(sampled)} entries from Tatoeba, "
            f"stratified across {len(unique_domains)} domain(s)."
        ),
    }


def build_all_corpora(
    language_codes: list[str],
    output_dir: Path,
    registry_path: Path | None = None,
    *,
    max_entries: int = 200,
    min_words: int = 3,
    max_words: int = 50,
    seed: int = 42,
    auto_yes: bool = False,
    probe_delay: float = 0.2,
) -> list[dict]:
    """Build development corpora for all viable Tatoeba pairs.

    Args:
        language_codes: List of ISO 639-3 codes to build pairs for.
        output_dir: Directory for corpus JSON files.
        registry_path: Path to registry.json to update.
        max_entries: Target entries per corpus.
        min_words: Minimum word count filter.
        max_words: Maximum word count filter.
        seed: Random seed for reproducible sampling.
        auto_yes: If True, skip the license confirmation prompt.
        probe_delay: Delay between probe requests.

    Returns:
        List of registry entry dicts for successfully built corpora.
    """
    # Step 1: Probe for available pairs
    print("=" * 60)
    print("  BATCH CORPUS BUILD — Tatoeba")
    print("=" * 60)
    print(f"\n  Languages: {len(language_codes)}")
    print(f"  Probing Tatoeba for available pairs...\n")

    viable_pairs = probe_all_pairs(
        language_codes,
        delay_seconds=probe_delay,
        progress=True,
    )

    if not viable_pairs:
        print("\n  No viable pairs found. Nothing to build.")
        return []

    # Deduplicate: only build each canonical direction once
    # (e.g., build eng→fra but not fra→eng as a separate corpus)
    seen_urls: set[str] = set()
    unique_pairs: list[PairProbe] = []
    for pair in viable_pairs:
        if pair.url not in seen_urls:
            seen_urls.add(pair.url)
            unique_pairs.append(pair)

    print(f"\n  Found {len(unique_pairs)} unique pair files.")

    # Step 2: License confirmation
    batch_license = LicenseInfo(
        source_name="Tatoeba",
        license_id="CC-BY-2.0",
        license_url="https://creativecommons.org/licenses/by/2.0/",
        source_url="https://tatoeba.org",
        download_url="(multiple files)",
    )
    if not confirm_batch_download(batch_license, len(unique_pairs), auto_yes=auto_yes):
        print("  Cancelled.")
        return []

    # Step 3: Build each corpus
    output_dir.mkdir(parents=True, exist_ok=True)
    built: list[dict] = []
    failed: list[str] = []
    skipped: list[str] = []

    for i, pair in enumerate(unique_pairs, 1):
        pair_label = f"{pair.source_lang}→{pair.target_lang}"
        size_label = f" ({pair.file_size_human})" if pair.file_size_human else ""
        print(f"\n  [{i}/{len(unique_pairs)}] {pair_label}{size_label}")

        result = _build_single_corpus(
            source_lang=pair.source_lang,
            target_lang=pair.target_lang,
            output_dir=output_dir,
            max_entries=max_entries,
            min_words=min_words,
            max_words=max_words,
            seed=seed,
        )

        if result:
            built.append(result)
            print(f"    ✅ {result['size']} entries written")
        else:
            skipped.append(pair_label)

    # Step 4: Update registry
    if registry_path and built:
        _update_registry(registry_path, built)

    # Step 5: Summary
    print("\n" + "=" * 60)
    print("  BUILD COMPLETE")
    print("=" * 60)
    print(f"  Built:   {len(built)} corpora")
    print(f"  Skipped: {len(skipped)} pairs (below minimum entry count)")
    if skipped:
        print(f"           {', '.join(skipped[:10])}")
        if len(skipped) > 10:
            print(f"           ... and {len(skipped) - 10} more")
    print("=" * 60)

    return built


def _update_registry(registry_path: Path, new_entries: list[dict]) -> None:
    """Update the corpus registry with newly built corpora.

    Reads the existing registry, adds new entries (or updates existing
    ones with matching IDs), and writes back.

    Args:
        registry_path: Path to registry.json.
        new_entries: List of registry entry dicts to add/update.
    """
    registry_path = Path(registry_path)

    # Load existing registry
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    else:
        registry = {"registry_version": "1.0.0", "datasets": []}

    # Build index of existing entries by ID for dedup
    existing_by_id: dict[str, int] = {}
    for idx, entry in enumerate(registry["datasets"]):
        existing_by_id[entry["id"]] = idx

    # Merge: update existing or append new
    for new_entry in new_entries:
        entry_id = new_entry["id"]
        if entry_id in existing_by_id:
            # Update in place
            registry["datasets"][existing_by_id[entry_id]] = new_entry
        else:
            registry["datasets"].append(new_entry)

    # Write back
    registry_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\n  Registry updated: {registry_path} ({len(registry['datasets'])} entries)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point for the batch builder."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Build development corpora for all viable Tatoeba pairs.",
    )
    parser.add_argument(
        "--language-cards-dir",
        required=True,
        help="Path to champollion language-cards directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="arena/datasets/curated",
        help="Output directory for corpus JSON files (default: arena/datasets/curated).",
    )
    parser.add_argument(
        "--registry",
        default=None,
        help="Path to registry.json to update.",
    )
    parser.add_argument(
        "--max-entries",
        type=int,
        default=200,
        help="Maximum entries per corpus (default: 200).",
    )
    parser.add_argument(
        "--min-words",
        type=int,
        default=3,
        help="Minimum words per entry (default: 3).",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=50,
        help="Maximum words per entry (default: 50).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42).",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip license confirmation prompt (for CI/automation).",
    )
    parser.add_argument(
        "--probe-delay",
        type=float,
        default=0.2,
        help="Delay between probe requests in seconds (default: 0.2).",
    )

    args = parser.parse_args()

    # Load language codes from cards
    codes = load_language_codes_from_cards(args.language_cards_dir)
    print(f"  Loaded {len(codes)} language codes from cards.")

    results = build_all_corpora(
        language_codes=codes,
        output_dir=Path(args.output_dir),
        registry_path=Path(args.registry) if args.registry else None,
        max_entries=args.max_entries,
        min_words=args.min_words,
        max_words=args.max_words,
        seed=args.seed,
        auto_yes=args.yes,
        probe_delay=args.probe_delay,
    )


if __name__ == "__main__":
    main()
