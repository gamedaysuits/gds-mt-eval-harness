"""
CLI entry point for the corpora builder.

Orchestrates the full corpus construction pipeline:
    1. Parse arguments and validate source-specific options
    2. Load the appropriate source adapter
    3. Fetch raw parallel entries from the source
    4. Filter entries by word count bounds
    5. Classify each entry's domain
    6. Estimate each entry's difficulty tier
    7. Infer register from domain classification
    8. Stratify and sample to match target distributions
    9. Output the final corpus as JSON
   10. Print summary statistics to stdout

This module is also the ``__main__`` target, so the package can be
invoked as ``python -m corpora_builder``.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from corpora_builder import __version__
from corpora_builder.adapters.base import RawEntry, SourceAdapter
from corpora_builder.difficulty_estimator import estimate_difficulty
from corpora_builder.domain_classifier import VALID_DOMAINS, classify_domain
from corpora_builder.licensing import (
    LicenseInfo,
    TATOEBA_LICENSE,
    build_tatoeba_url,
    confirm_download,
)
from corpora_builder.schema import Corpus, CorpusEntry


# ---------------------------------------------------------------------------
# Register-inference mapping
# ---------------------------------------------------------------------------
# Maps domain codes to their most likely writing register. This is a
# simplification — real register detection would require stylistic
# analysis — but it's a reasonable default that saves manual annotation
# and can be overridden per-entry later.
#
# The mapping reflects typical register for each domain:
#   - UI strings, support tickets, and e-commerce text are functional
#   - Legal, medical, and scientific text is formal/technical
#   - Subtitles and conversational text are casual

_DOMAIN_TO_REGISTER: dict[str, str] = {
    "ui": "technical",
    "legal": "formal",
    "medical": "technical",
    "financial": "formal",
    "edu": "formal",
    "ecommerce": "functional",
    "marketing": "persuasive",
    "gov": "formal",
    "scientific": "technical",
    "religious": "formal",
    "support": "functional",
    "subtitles": "conversational",
    "news": "formal",
    "literary": "literary",
    "conv": "conversational",
    "tech": "technical",
}


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Arguments are grouped logically:
        - Required: source, languages, output path
        - Source-specific: OPUS corpus name, CSV file path
        - Filtering: word count bounds
        - Sampling: max entries, random seed
    """
    parser = argparse.ArgumentParser(
        prog="build-corpus",
        description=(
            "Build a structured evaluation corpus from parallel text sources. "
            "Imports human-authored text, classifies by domain and difficulty, "
            "and outputs corpus JSON for the MT Eval Arena."
        ),
    )

    # --- Required arguments ---
    parser.add_argument(
        "--source",
        required=True,
        choices=["tatoeba", "opus", "csv"],
        help="Source adapter to use for fetching parallel text.",
    )
    parser.add_argument(
        "--source-lang",
        required=True,
        help="ISO 639-3 code for the source language (e.g. 'eng').",
    )
    parser.add_argument(
        "--target-lang",
        required=True,
        help="ISO 639-3 code for the target language (e.g. 'fra').",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the output corpus JSON file.",
    )

    # --- Source-specific arguments ---
    parser.add_argument(
        "--opus-corpus",
        default=None,
        help=(
            "OPUS sub-corpus name (e.g. 'GNOME', 'KDE4', 'QED'). "
            "Required when --source is 'opus'."
        ),
    )
    parser.add_argument(
        "--csv-file",
        default=None,
        help=(
            "Path to a custom CSV file with parallel text. "
            "Required when --source is 'csv'."
        ),
    )

    # --- Filtering arguments ---
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

    # --- Sampling arguments ---
    parser.add_argument(
        "--max-entries",
        type=int,
        default=200,
        help="Maximum number of entries in the output corpus (default: 200).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sampling (default: 42).",
    )

    # --- License / download arguments ---
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip license confirmation prompt (for CI/automation).",
    )

    return parser


def _validate_args(args: argparse.Namespace) -> None:
    """Validate source-specific argument requirements.

    Some arguments are conditionally required depending on the
    chosen source adapter. argparse doesn't support conditional
    requirements natively, so we validate them here with clear
    error messages.

    Raises:
        SystemExit: If validation fails (via parser.error-style messages).
    """
    if args.source == "opus" and args.opus_corpus is None:
        print(
            "Error: --opus-corpus is required when --source is 'opus'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.source == "csv" and args.csv_file is None:
        print(
            "Error: --csv-file is required when --source is 'csv'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.min_words < 1:
        print("Error: --min-words must be at least 1.", file=sys.stderr)
        sys.exit(1)

    if args.max_words < args.min_words:
        print(
            "Error: --max-words must be >= --min-words.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.max_entries < 1:
        print("Error: --max-entries must be at least 1.", file=sys.stderr)
        sys.exit(1)


def _load_adapter(source_name: str) -> SourceAdapter:
    """Load a source adapter by name.

    Adapters are imported lazily to avoid pulling in dependencies
    for sources that aren't being used. Each adapter module registers
    itself by providing a concrete ``SourceAdapter`` subclass.

    Args:
        source_name: One of ``"tatoeba"``, ``"opus"``, ``"csv"``.

    Returns:
        An instantiated SourceAdapter ready to fetch data.

    Raises:
        SystemExit: If the adapter module is not yet implemented.
    """
    # Lazy imports — only load the adapter that's actually needed.
    # This keeps startup fast and avoids import errors for adapters
    # whose dependencies aren't installed.
    if source_name == "tatoeba":
        from corpora_builder.adapters.tatoeba_adapter import TatoebaAdapter
        return TatoebaAdapter()
    elif source_name == "opus":
        from corpora_builder.adapters.opus_adapter import OpusAdapter
        return OpusAdapter()
    elif source_name == "csv":
        from corpora_builder.adapters.csv_adapter import CsvAdapter
        return CsvAdapter()
    else:
        # This branch should be unreachable because argparse enforces
        # the choices, but explicit handling prevents silent failures
        # if someone calls _load_adapter() directly.
        print(f"Error: Unknown source adapter '{source_name}'.", file=sys.stderr)
        sys.exit(1)


def _filter_by_word_count(
    entries: list[RawEntry],
    min_words: int,
    max_words: int,
) -> list[RawEntry]:
    """Filter entries to those within the word count bounds.

    Word count is based on the source text (typically English),
    since that's the language our difficulty estimator is calibrated
    for. We don't filter on target text word count because
    agglutinative languages can have very different token counts
    for semantically equivalent text.

    Args:
        entries: Raw entries from the source adapter.
        min_words: Minimum word count (inclusive).
        max_words: Maximum word count (inclusive).

    Returns:
        Filtered list of entries.
    """
    filtered: list[RawEntry] = []
    for entry in entries:
        word_count = len(entry.source_text.split())
        if min_words <= word_count <= max_words:
            filtered.append(entry)
    return filtered


def _enrich_entry(
    raw: RawEntry,
    adapter_name: str,
) -> CorpusEntry:
    """Transform a raw entry into a fully enriched corpus entry.

    Applies domain classification, difficulty estimation, and
    register inference. Each transformation is a pure function
    call — no side effects, no network requests.

    Args:
        raw: The raw parallel text entry from a source adapter.
        adapter_name: Name of the source adapter, used to construct
            the entry ID and provenance.

    Returns:
        A fully populated CorpusEntry.
    """
    # Classify domain from the source text (English-centric keywords)
    classification = classify_domain(raw.source_text)
    domain = classification.domain

    # Estimate difficulty from the source text
    difficulty_result = estimate_difficulty(raw.source_text)

    # Infer register from domain — crash if the domain isn't in the map,
    # because that means VALID_DOMAINS and _DOMAIN_TO_REGISTER are out of sync
    if domain not in _DOMAIN_TO_REGISTER:
        raise ValueError(
            f"Domain '{domain}' has no register mapping in _DOMAIN_TO_REGISTER. "
            f"This is a bug — every domain in VALID_DOMAINS must have a register mapping."
        )
    register = _DOMAIN_TO_REGISTER[domain]

    # Build the unique entry ID: adapter name + source-specific ID
    entry_id = f"{adapter_name}_{raw.source_id}"

    # Build provenance from the raw entry's metadata
    provenance: dict[str, Any] = {
        "source_name": adapter_name,
        "source_id": raw.source_id,
        "license": raw.metadata.get("license", "unknown"),
        "url": raw.metadata.get("url", ""),
    }

    # Store classification and difficulty details in metadata
    # so downstream consumers can audit how entries were tagged
    enrichment_metadata: dict[str, Any] = {
        **raw.metadata,
        "classification_confidence": classification.confidence,
        "difficulty_word_count": difficulty_result.word_count,
        "difficulty_estimated_clauses": difficulty_result.estimated_clauses,
        "difficulty_avg_word_length": difficulty_result.avg_word_length,
    }

    return CorpusEntry(
        id=entry_id,
        source=raw.source_text,
        reference=raw.target_text,
        domain=domain,
        difficulty=difficulty_result.tier,
        register=register,
        provenance=provenance,
        metadata=enrichment_metadata,
    )


def _stratified_sample(
    entries: list[CorpusEntry],
    max_entries: int,
    rng: random.Random,
) -> list[CorpusEntry]:
    """Sample entries with stratification across domains and difficulty tiers.

    The goal is a balanced corpus that covers as many domains and
    difficulty levels as possible, rather than being dominated by
    whatever domain the source happens to have the most data for.

    Strategy:
        1. Group entries by (domain, difficulty) pair.
        2. Compute a per-group quota: max_entries / number_of_groups,
           rounded up.
        3. Sample up to the quota from each group.
        4. If the total exceeds max_entries, trim by randomly removing
           entries from the largest groups first.

    This produces a more uniform distribution than simple random
    sampling, which would over-represent the dominant domain.

    Args:
        entries: All enriched entries (post-filtering, pre-sampling).
        max_entries: Target corpus size.
        rng: Seeded Random instance for reproducibility.

    Returns:
        A list of at most ``max_entries`` entries, stratified across
        domains and difficulty tiers.
    """
    if len(entries) <= max_entries:
        # Not enough entries to require sampling — return all of them
        return list(entries)

    # Group entries by (domain, difficulty) for stratification
    groups: dict[tuple[str, int], list[CorpusEntry]] = {}
    for entry in entries:
        key = (entry.domain, entry.difficulty)
        if key not in groups:
            groups[key] = []
        groups[key].append(entry)

    # Compute per-group quota — how many entries each group should
    # contribute to a balanced corpus
    num_groups = len(groups)
    base_quota = max_entries // num_groups
    # Distribute the remainder across the first N groups
    remainder = max_entries % num_groups

    sampled: list[CorpusEntry] = []
    group_keys = sorted(groups.keys())

    for i, key in enumerate(group_keys):
        group = groups[key]
        # Give one extra entry to the first `remainder` groups
        quota = base_quota + (1 if i < remainder else 0)
        # Sample up to the quota from this group
        if len(group) <= quota:
            sampled.extend(group)
        else:
            sampled.extend(rng.sample(group, quota))

    # Final trim: if rounding caused us to exceed max_entries
    if len(sampled) > max_entries:
        sampled = rng.sample(sampled, max_entries)

    return sampled


def _print_summary(corpus: Corpus) -> None:
    """Print human-readable summary statistics to stdout.

    Covers: total entries, language pair, domain distribution,
    difficulty distribution, and per-domain entry counts.
    """
    print("\n" + "=" * 60)
    print("  CORPUS BUILD SUMMARY")
    print("=" * 60)
    print(f"  Corpus ID:     {corpus.corpus_id}")
    print(f"  Version:       {corpus.version}")
    print(
        f"  Language pair:  {corpus.language_pair['source']} → "
        f"{corpus.language_pair['target']}"
    )
    print(f"  Segment:       {corpus.segment}")
    print(f"  Total entries: {corpus.entry_count}")
    print(f"  Created:       {corpus.created}")

    # Domain distribution
    domain_counts = Counter(entry.domain for entry in corpus.entries)
    print(f"\n  Domains ({len(domain_counts)} unique):")
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {domain:<12} {count:>4}  {bar}")

    # Difficulty distribution
    diff_counts = Counter(entry.difficulty for entry in corpus.entries)
    print("\n  Difficulty tiers:")
    for tier in range(1, 6):
        count = diff_counts.get(tier, 0)
        bar = "█" * count
        print(f"    Tier {tier}       {count:>4}  {bar}")

    # Register distribution
    reg_counts = Counter(entry.register for entry in corpus.entries)
    print(f"\n  Registers ({len(reg_counts)} unique):")
    for register, count in sorted(reg_counts.items(), key=lambda x: -x[1]):
        print(f"    {register:<16} {count:>4}")

    print("=" * 60 + "\n")


def main() -> None:
    """Main entry point for the corpus builder CLI.

    Orchestrates the full pipeline: parse args → load adapter → fetch →
    filter → enrich → sample → output → report.
    """
    parser = _build_parser()
    args = parser.parse_args()
    _validate_args(args)

    # Seed the RNG for reproducible sampling
    rng = random.Random(args.seed)

    # --- Step 1: Load the source adapter ---
    print(f"Loading '{args.source}' adapter...")
    adapter = _load_adapter(args.source)

    # --- Step 1.5: License confirmation before download ---
    # For Tatoeba: auto-construct the download URL and show license info.
    # For other sources: show the adapter's license metadata.
    if args.source == "tatoeba":
        download_url = build_tatoeba_url(args.source_lang, args.target_lang)
        license_info = LicenseInfo(
            source_name="Tatoeba",
            license_id="CC-BY-2.0",
            license_url="https://creativecommons.org/licenses/by/2.0/",
            source_url="https://tatoeba.org",
            download_url=download_url,
        )
        if not confirm_download(license_info, auto_yes=args.yes):
            print("  Cancelled.")
            sys.exit(0)
    else:
        # For non-Tatoeba sources, the user already has a local file.
        # No download occurs, so no license confirmation needed here.
        # The adapter's license is recorded in provenance.
        download_url = None

    # --- Step 2: Fetch raw entries ---
    print(
        f"Fetching parallel text: {args.source_lang} → {args.target_lang}..."
    )

    # Build adapter-specific kwargs
    fetch_kwargs: dict[str, Any] = {}
    if args.source == "tatoeba" and download_url is not None:
        # Auto-constructed URL — pass it to the adapter
        fetch_kwargs["download_url"] = download_url
    if args.source == "opus" and args.opus_corpus is not None:
        fetch_kwargs["corpus_name"] = args.opus_corpus
    if args.source == "csv" and args.csv_file is not None:
        fetch_kwargs["csv_path"] = args.csv_file

    raw_entries = adapter.fetch(
        source_lang=args.source_lang,
        target_lang=args.target_lang,
        **fetch_kwargs,
    )
    print(f"  Fetched {len(raw_entries)} raw entries.")

    # --- Step 3: Filter by word count ---
    filtered = _filter_by_word_count(raw_entries, args.min_words, args.max_words)
    removed_count = len(raw_entries) - len(filtered)
    print(
        f"  After word count filter ({args.min_words}–{args.max_words} words): "
        f"{len(filtered)} entries ({removed_count} removed)."
    )

    if not filtered:
        print(
            "Error: No entries remain after filtering. "
            "Try adjusting --min-words / --max-words or using a different source.",
            file=sys.stderr,
        )
        sys.exit(1)

    # --- Step 4: Enrich entries (domain + difficulty + register) ---
    print("  Classifying domains and estimating difficulty...")
    enriched: list[CorpusEntry] = []
    for raw in filtered:
        enriched_entry = _enrich_entry(raw, adapter.name)
        enriched.append(enriched_entry)

    # --- Step 5: Stratified sampling ---
    sampled = _stratified_sample(enriched, args.max_entries, rng)
    print(
        f"  Sampled {len(sampled)} entries "
        f"(target: {args.max_entries}, seed: {args.seed})."
    )

    # --- Step 6: Build the Corpus object ---
    # Collect unique domains present in the final sample
    unique_domains = sorted(set(entry.domain for entry in sampled))

    now_utc = datetime.now(timezone.utc).isoformat()

    corpus = Corpus(
        corpus_id=f"{args.source}-{args.source_lang}-{args.target_lang}",
        version=__version__,
        language_pair={
            "source": args.source_lang,
            "target": args.target_lang,
        },
        segment="development",
        created=now_utc,
        entry_count=len(sampled),
        domains=unique_domains,
        entries=sampled,
        provenance={
            "builder": "champollion-corpora-builder",
            "builder_version": __version__,
            "source_adapter": args.source,
            "seed": args.seed,
            "min_words": args.min_words,
            "max_words": args.max_words,
        },
    )

    # --- Step 7: Write output ---
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    corpus.to_json(output_path)
    print(f"\n  Corpus written to: {output_path.resolve()}")

    # --- Step 8: Print summary ---
    _print_summary(corpus)


if __name__ == "__main__":  # pragma: no cover
    # `python -m corpora_builder.cli` must behave exactly like the
    # `build-corpus` console script — a silent no-op here cost a corpus
    # rebuild that never happened (eng-tuk, 2026-06-12).
    main()
