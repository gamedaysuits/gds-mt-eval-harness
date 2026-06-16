"""
Corpus Loader — Multi-format dataset loading for the eval harness.

Supports four corpus formats, auto-detected by file extension and content:

    Format            Extension      Detection
    ─────────────     ─────────      ──────────────────────────────────
    Harness JSON      .json          Has "entries" key or list of dicts
    JSONL             .jsonl         One JSON object per line
    TSV               .tsv / .tab    Tab-separated columns
    Parallel text     (two files)    --source-file + --reference-file

All formats are normalized to the harness's internal shape:
    [{"id": int, "source": str, "reference": str, ...}]

Design decisions:
    - Auto-ID: All formats get sequential 0-indexed IDs if not present.
    - Metadata pass-through: Extra fields in JSON/JSONL are preserved.
    - Header detection for TSV: If row 0 contains "source"/"reference"
      (case-insensitive), treat as header row and use column names.
    - Parallel text: Both files must have identical line counts. Empty
      lines are preserved (they may be intentional paragraph breaks in
      some corpora like FLORES+).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mt_eval_harness.config import RunConfig


# ---------------------------------------------------------------------------
# Format-specific loaders
# ---------------------------------------------------------------------------

def _load_harness_json(path: Path, config: RunConfig) -> tuple[list[dict], dict]:
    """Load the harness's native JSON format.

    Supports two shapes:
        - Wrapped:  {"dataset": {...}, "entries": [...]}
        - Flat:     [{"source": ..., "reference": ...}, ...]

    Returns:
        (entries, dataset_metadata) — metadata dict may be empty for flat format.
    """
    try:
        corpus = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        # A truncated download or hand-edited corpus must abort with a
        # human-readable message, not a raw decoder traceback.
        raise SystemExit(
            f"\n  ❌ ERROR: corpus file is not valid JSON: {path}\n"
            f"  {exc}\n"
            f"  Re-download or fix the file, then re-run."
        )

    if isinstance(corpus, dict) and "entries" in corpus:
        dataset_meta = corpus.get("dataset", {})
        entries = corpus["entries"]
        return entries, dataset_meta

    if isinstance(corpus, list):
        return corpus, {}

    raise ValueError(
        f"Unrecognized JSON structure in {path}. "
        f"Expected a list of entries or an object with an 'entries' key."
    )


def _load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file (one JSON object per line).

    Common in HuggingFace datasets and many NLP tools.
    Lines that are empty or whitespace-only are skipped.
    """
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON on line {line_num + 1} of {path}: {e}"
                ) from e
            entries.append(entry)
    return entries


def _load_tsv(path: Path) -> list[dict]:
    """Load a TSV (tab-separated values) file.

    Header detection: If the first row contains "source" and "reference"
    (case-insensitive), it's treated as a header and column names are used.
    Otherwise, column 0 = source, column 1 = reference.

    Extra columns beyond the first two are preserved as "col_2", "col_3", etc.
    unless headers are present, in which case the header names are used.
    """
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        rows = list(reader)

    if not rows:
        return []

    # Check for header row
    first_row_lower = [cell.strip().lower() for cell in rows[0]]
    has_header = "source" in first_row_lower

    if has_header:
        headers = [cell.strip() for cell in rows[0]]
        data_rows = rows[1:]
    else:
        # Default column mapping: col 0 = source, col 1 = reference
        headers = ["source", "reference"] + [
            f"col_{i}" for i in range(2, len(rows[0]))
        ]
        data_rows = rows

    entries = []
    for row in data_rows:
        if not row or all(cell.strip() == "" for cell in row):
            continue
        entry = {}
        for i, cell in enumerate(row):
            if i < len(headers):
                entry[headers[i]] = cell
            else:
                entry[f"col_{i}"] = cell
        entries.append(entry)

    return entries


def _load_parallel_text(
    source_path: Path,
    reference_path: Path,
) -> list[dict]:
    """Load parallel text files (one sentence per line, aligned by line number).

    This is the standard format for MT evaluation corpora:
    FLORES+, WMT, NTREX, Tatoeba, OPUS all ship this way.

    Both files must have the same number of lines. Empty lines are
    preserved since they may represent intentional segment boundaries.
    """
    source_lines = source_path.read_text(encoding="utf-8").splitlines()
    reference_lines = reference_path.read_text(encoding="utf-8").splitlines()

    if len(source_lines) != len(reference_lines):
        raise ValueError(
            f"Line count mismatch: {source_path} has {len(source_lines)} lines, "
            f"{reference_path} has {len(reference_lines)} lines. "
            f"Parallel text files must have identical line counts."
        )

    entries = []
    for i, (src, ref) in enumerate(zip(source_lines, reference_lines)):
        entries.append({
            "id": i,
            "source": src,
            "reference": ref,
        })

    return entries


# ---------------------------------------------------------------------------
# Unified entry point
# ---------------------------------------------------------------------------

def _ensure_ids(entries: list[dict]) -> list[dict]:
    """Ensure every entry has an 'id' field.

    If entries already have IDs, they're preserved. If not, sequential
    0-indexed IDs are assigned. Mixed (some have IDs, some don't) is
    treated as "no IDs" to avoid conflicts.
    """
    has_ids = all("id" in e for e in entries)
    if has_ids:
        return entries

    for i, entry in enumerate(entries):
        if "id" not in entry:
            entry["id"] = i
    return entries


def load_corpus(config: RunConfig) -> tuple[list[dict], dict]:
    """Load entries from a corpus in any supported format.

    Format resolution:
        1. If config.source_file and config.reference_file are set,
           load as parallel text (ignores config.corpus_path).
        2. Otherwise, detect format from config.corpus_path extension:
           - .jsonl → JSONL
           - .tsv / .tab → TSV
           - .json (default) → Harness JSON

    After loading, applies dataset filtering (segments, ID ranges, etc.)
    and auto-populates config metadata from corpus when available.

    Args:
        config: RunConfig with corpus_path or source_file + reference_file set.

    Returns:
        Tuple of (entries, dataset_metadata).
        - entries: List of entry dicts, each with at least {id, source, reference}.
        - dataset_metadata: Dict from the corpus envelope (id, version,
          language_pair, etc.). Empty dict for formats without envelopes
          (JSONL, TSV, parallel text).
    """
    # --- Parallel text mode ---
    if config.source_file and config.reference_file:
        src = Path(config.source_file)
        ref = Path(config.reference_file)
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")
        if not ref.exists():
            raise FileNotFoundError(f"Reference file not found: {ref}")

        print(f"  Format:      parallel text")
        print(f"  Source:      {src}")
        print(f"  Reference:   {ref}")

        entries = _load_parallel_text(src, ref)
        entries = _ensure_ids(entries)
        return _apply_filters(entries, config), {}

    # --- Single file mode ---
    if not config.corpus_path:
        raise FileNotFoundError(
            "No corpus specified. Use --corpus <path> or "
            "--source-file <src> --reference-file <ref>."
        )

    corpus_path = Path(config.corpus_path)
    if not corpus_path.exists():
        # Fetch-from-source: a missing corpus may be described by a
        # corpora card (cli/shared/corpora-cards/) with a `source`
        # block — Champollion doesn't host third-party corpora, it
        # rebuilds them from the upstream repo into a gitignored cache
        # (arena/datasets/.cache/).
        from mt_eval_harness.corpus_fetch import try_fetch_missing_corpus

        fetched = try_fetch_missing_corpus(
            corpus_path,
            assume_yes=getattr(config, "assume_yes", False),
        )
        if fetched is None:
            raise FileNotFoundError(f"Corpus not found: {corpus_path}")
        print(f"  Corpus:      fetched from source → {fetched}")
        corpus_path = fetched
        config.corpus_path = str(fetched)

    suffix = corpus_path.suffix.lower()

    if suffix == ".jsonl":
        print(f"  Format:      JSONL")
        entries = _load_jsonl(corpus_path)
        dataset_meta = {}

    elif suffix in (".tsv", ".tab"):
        print(f"  Format:      TSV")
        entries = _load_tsv(corpus_path)
        dataset_meta = {}

    else:
        # Default: harness JSON (.json or anything else)
        entries, dataset_meta = _load_harness_json(corpus_path, config)

        # Auto-populate config from corpus metadata when not set explicitly.
        # This means users can just --corpus <file> without extra flags.
        #
        # language_pair can live in two places depending on corpus format:
        #   - Inside dataset_meta (e.g. {"dataset": {"language_pair": {...}}})
        #   - At the top level of the corpus JSON (Tatoeba corpora use this)
        lang_pair = dataset_meta.get("language_pair", {})
        if not lang_pair:
            # Check top-level corpus object for language_pair
            # (Tatoeba corpora store it at root, not inside dataset)
            raw = json.loads(corpus_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                lang_pair = raw.get("language_pair", {})

        if dataset_meta:
            if not config.dataset_id and dataset_meta.get("id"):
                config.dataset_id = dataset_meta["id"]
                print(f"  Dataset ID:  {config.dataset_id} (from corpus metadata)")

        if not config.target_lang.strip() and lang_pair.get("target_name"):
            config.target_lang = lang_pair["target_name"]
            print(f"  Target lang: {config.target_lang} (from corpus metadata)")

        if not config.source_lang.strip() and lang_pair.get("source_name"):
            config.source_lang = lang_pair["source_name"]
            print(f"  Source lang: {config.source_lang} (from corpus metadata)")

        # ISO codes for self-contained MT adapters (read by
        # methods/base_http_mt._resolve_lang_codes). The corpus language_pair
        # carries them as source/target; only set when not supplied explicitly
        # (e.g. via --source-code/--target-code).
        if not getattr(config, "source_code", "") and lang_pair.get("source"):
            config.source_code = lang_pair["source"]
        if not getattr(config, "target_code", "") and lang_pair.get("target"):
            config.target_code = lang_pair["target"]

    entries = _ensure_ids(entries)
    return _apply_filters(entries, config), dataset_meta


def _apply_filters(entries: list[dict], config: RunConfig) -> list[dict]:
    """Apply dataset filtering: segment names, ID ranges, explicit IDs.

    This is the filtering logic that was previously inline in runner.py's
    load_corpus(). Extracted here so all formats share the same filtering.
    """
    # Auto-detect segment names from corpus if not explicitly configured.
    segment_names = config.segment_names
    if not segment_names:
        segment_names = sorted({
            e.get("segment", "") for e in entries if e.get("segment")
        })
        if segment_names:
            print(f"  Auto-detected segments: {', '.join(segment_names)}")

    # Explicit entry IDs take precedence
    if config.entry_ids is not None:
        # String-normalize both sides: corpora store ids as ints (EdTeKLA)
        # or strings (Tatoeba 'tatoeba_2289'), and CLI input arrives as
        # text. Exact-type matching silently selected nothing.
        id_set = {str(i) for i in config.entry_ids}
        filtered = [e for e in entries if str(e["id"]) in id_set]
        if len(filtered) != len(id_set):
            found = {str(e["id"]) for e in filtered}
            missing = id_set - found
            print(f"  WARNING: {len(missing)} entry IDs not found: {sorted(missing)[:10]}")
        return filtered

    dataset = config.dataset.strip().lower()

    if dataset == "all":
        return entries

    # Check for segment name (case-insensitive — corpus segments may be
    # mixed case like "Development" while CLI input is lowercased)
    segment_names_lower = {s.lower(): s for s in segment_names}
    if dataset in segment_names_lower:
        actual_name = segment_names_lower[dataset]
        return [e for e in entries if e.get("segment") == actual_name]

    # Check for ID range (e.g., "0-61")
    if "-" in dataset:
        try:
            start, end = dataset.split("-")
            start, end = int(start), int(end)
            return [e for e in entries if start <= e["id"] <= end]
        except (ValueError, IndexError):
            pass

    # Check for single ID
    try:
        single_id = int(dataset)
        return [e for e in entries if e["id"] == single_id]
    except ValueError:
        pass

    available = ', '.join(segment_names) if segment_names else 'none detected'
    raise ValueError(
        f"Unknown dataset filter: '{config.dataset}'. "
        f"Use 'all', a segment name ({available}), "
        f"an ID range ('0-61'), or a single ID."
    )
