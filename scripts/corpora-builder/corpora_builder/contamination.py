"""
Test-set contamination checker for evaluation corpora.

Verifies that sealed evaluation segments (``held_out`` and
``gold_standard``) do not overlap with development / public corpora.
Any such overlap silently inflates benchmark scores: a model (or a
prompt engineer) that has seen a held-out sentence during development
is no longer being tested on unseen data. For a benchmark that will be
cited in front of reviewers, this is a credibility-critical property,
so it must be checked mechanically rather than by convention.

How matching works
------------------
Every entry's ``source`` and ``reference`` texts are normalized
(NFC unicode normalization, casefold, whitespace collapse, terminal
punctuation strip) and hashed:

    - **exact-pair fingerprint** — SHA-256 of
      ``normalized_source + "\\t" + normalized_reference``. Two entries
      sharing this fingerprint are the same translation pair.
    - **source-only fingerprint** — SHA-256 of the normalized source
      alone. Catches same-source-different-reference leakage, where a
      sealed source sentence appears in a public set with a different
      translation. The source sentence itself is the leaked asset.

Severity model
--------------
    - ``CRITICAL`` — a sealed entry (``held_out`` / ``gold_standard``)
      overlaps a development or public set. This is the failure mode
      the checker exists to catch.
    - ``WARNING``  — two *sealed* segments overlap each other. Not a
      public leak, but sealed sets are supposed to be disjoint;
      duplicated sealed entries double-count in aggregate metrics.
    - ``INFO``     — development↔development cross-corpus duplicates,
      and source-only overlaps between corpora with *different* target
      languages (the same English sentence legitimately appears in
      many Tatoeba-derived dev sets; that is not leakage for any one
      target language's sealed data).

Segments that cannot be determined are treated as ``development`` for
severity purposes. This is the conservative choice: an unknown-segment
corpus overlapping a sealed set is flagged CRITICAL rather than
silently ignored.

Defensive loading
-----------------
Corpus files in the wild come in several shapes — the canonical
``Corpus`` schema (see ``schema.py``), older ``{"dataset": ...,
"entries": [...]}`` wrappers, per-entry ``segment`` fields, and plain
entry lists. The loader handles all of them and skips (with a note)
anything it cannot interpret, rather than crashing mid-audit.

Report hygiene
--------------
The markdown report **never prints sentence text** — only entry ids,
corpus names, and counts. Sealed content must not leak into a report
that gets committed to the repository; that would itself be
contamination.

CLI usage::

    python3 -m corpora_builder.contamination <files-dirs-or-globs...> \\
        --report docs/CONTAMINATION_REPORT.md  # internal wiki, not arena/datasets/

Exit status is 1 if any CRITICAL finding exists, so the checker can
gate CI.
"""

from __future__ import annotations

import argparse
import glob as _glob
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Severity levels and segment taxonomy
# ---------------------------------------------------------------------------
# Canonical segment names follow schema.py's three defaults. "unknown"
# is the explicit fallback when no segment can be inferred; it is
# treated as non-sealed (i.e. like development) for severity, which is
# the conservative direction — see module docstring.
# ---------------------------------------------------------------------------

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"

_SEVERITY_ORDER = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2}

SEALED_SEGMENTS: frozenset[str] = frozenset({"held_out", "gold_standard"})

#: Maximum example id-pairs retained per finding in the report.
MAX_EXAMPLES = 20


# ---------------------------------------------------------------------------
# Text normalization and fingerprinting
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"\s+")

# Sentence-terminal punctuation stripped from the end of normalized
# text. Includes ASCII, CJK fullwidth, Arabic question mark, ellipsis,
# and Spanish inverted marks (which can trail in informal text). We
# deliberately do NOT strip commas/semicolons mid-strength punctuation:
# "wait," vs "wait" differing only by a comma is a stretch for "same
# sentence", while "Come." vs "Come" plainly is the same sentence.
_TERMINAL_PUNCT = ".!?…。．！？؟¡¿"


def normalize_text(text: str) -> str:
    """Normalize text for duplicate detection.

    Applies, in order: NFC unicode normalization, casefold, whitespace
    collapse (all runs of whitespace become a single space, leading and
    trailing whitespace removed), and terminal punctuation stripping.

    Casefold (rather than lower) handles full unicode case mapping,
    e.g. German eszett. NFC matters for languages like Plains Cree SRO
    where "ê" may be stored composed or decomposed depending on which
    tool produced the file.

    Args:
        text: Raw source or reference text.

    Returns:
        The normalized text. May be empty if the input was only
        whitespace and punctuation.
    """
    normalized = unicodedata.normalize("NFC", text).casefold()
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()
    normalized = normalized.rstrip(_TERMINAL_PUNCT).rstrip()
    return normalized


def pair_fingerprint(source: str, reference: str) -> str:
    """SHA-256 fingerprint of a normalized (source, reference) pair.

    The two normalized texts are joined with a tab, which cannot occur
    in normalized text (whitespace collapse replaces tabs), so the
    fingerprint is unambiguous — ("a b", "c") can never collide with
    ("a", "b c").

    Args:
        source: Raw source text.
        reference: Raw reference translation.

    Returns:
        Hex digest string.
    """
    payload = normalize_text(source) + "\t" + normalize_text(reference)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def source_fingerprint(source: str) -> str:
    """SHA-256 fingerprint of the normalized source text alone.

    Used to catch same-source-different-reference leakage.

    Args:
        source: Raw source text.

    Returns:
        Hex digest string.
    """
    return hashlib.sha256(normalize_text(source).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Segment inference
# ---------------------------------------------------------------------------

def canonical_segment(raw: str | None) -> str:
    """Map a raw segment label to a canonical segment name.

    Handles the variety of labels found in real files:
    ``"gold_standard"``, ``"held_out"``, ``"holdout"``, per-entry
    labels like ``"phase1_test"`` / ``"textbook_remainder"`` from
    master corpora, and split names like ``"dev"``.

    Tokens are matched against the label's words so that e.g.
    ``"textbook_test"`` maps to held_out but ``"attestation"`` (which
    merely contains the substring "test") would not.

    Args:
        raw: Raw segment string, or None.

    Returns:
        One of ``"gold_standard"``, ``"held_out"``, ``"development"``,
        or ``"unknown"``.
    """
    if not raw:
        return "unknown"
    label = raw.strip().lower()
    tokens = set(re.split(r"[^a-z0-9]+", label)) - {""}

    # "full_minus_holdout" style names *negate* the holdout token:
    # the file is everything EXCEPT the holdout, i.e. development.
    negated = bool(tokens & {"minus", "excl", "excluding", "without", "no"})

    # Prefix match so numbered tokens like "gold62" still classify.
    if any(token.startswith("gold") for token in tokens):
        return "gold_standard"
    if not negated and any(
        token.startswith(("held", "heldout", "holdout")) or token == "test"
        for token in tokens
    ):
        return "held_out"
    if tokens & {"dev", "development", "train", "training", "sample",
                 "remainder", "curated", "master", "full"}:
        return "development"
    return "unknown"


def is_quarantined(path_or_name: str | Path) -> bool:
    """True when a corpus path sits inside a ``quarantine/`` directory.

    Quarantined corpora are sets with *verified* contamination that are
    deliberately kept (untracked) for historical reproducibility but
    must never be used for held-out evaluation. Findings that involve
    them are still reported — the contamination is real — but the
    report annotates them so readers know the overlap is documented
    and the file is already withdrawn from evaluation use.
    """
    return "quarantine" in Path(path_or_name).parts


def infer_file_segment(path: Path, corpus_meta: dict[str, Any]) -> str:
    """Infer the default segment for all entries in a corpus file.

    Precedence:
        1. Explicit corpus-level ``segment`` field (canonical schema).
        2. Filename heuristics (``textbook_test`` → held_out, etc.).
        3. Parent directory name (files under ``held_out/`` are
           held_out even if the filename says nothing).
        4. ``"unknown"``.

    Per-entry ``segment`` fields override this default per entry; that
    is handled by the loader, not here.

    Args:
        path: Path of the corpus JSON file.
        corpus_meta: Top-level dict of the parsed file (may be empty
            for plain-list files).

    Returns:
        Canonical segment name.
    """
    explicit = corpus_meta.get("segment")
    if isinstance(explicit, str) and explicit.strip():
        return canonical_segment(explicit)

    from_name = canonical_segment(path.stem)
    if from_name != "unknown":
        return from_name

    for parent in path.parents:
        from_dir = canonical_segment(parent.name)
        if from_dir != "unknown":
            return from_dir
        # Stop climbing once we leave dataset-ish directories; the
        # repository root's name should not influence classification.
        if parent.name in ("datasets", ""):
            break
    return "unknown"


# ---------------------------------------------------------------------------
# Defensive corpus loading
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EntryRecord:
    """A loaded corpus entry, reduced to what contamination needs.

    Attributes:
        corpus: Display name of the owning corpus (relative path).
        segment: Canonical segment of this entry.
        entry_id: Entry id as a string (ids are ints in older files).
        pair_fp: Exact-pair fingerprint.
        source_fp: Source-only fingerprint.
        lang_pair: ``(source_iso, target_iso)`` if known, else None.
    """

    corpus: str
    segment: str
    entry_id: str
    pair_fp: str
    source_fp: str
    lang_pair: tuple[str, str] | None

    @property
    def sealed(self) -> bool:
        return self.segment in SEALED_SEGMENTS


def _extract_language_pair(data: dict[str, Any]) -> tuple[str, str] | None:
    """Pull a (source_iso, target_iso) pair out of whatever shape the
    file uses, if any. Checks the canonical top-level ``language_pair``
    and the older ``dataset.language_pair`` nesting; accepts either
    ``source``/``target`` or ``source_iso``/``target_iso`` keys.
    """
    for container in (data, data.get("dataset") or {}):
        if not isinstance(container, dict):
            continue
        lp = container.get("language_pair")
        if not isinstance(lp, dict):
            continue
        src = lp.get("source_iso") or lp.get("source")
        tgt = lp.get("target_iso") or lp.get("target")
        if isinstance(src, str) and isinstance(tgt, str):
            # Some files store full names ("English") in source/target
            # with the ISO codes in *_iso. Only trust short codes.
            if len(src) <= 3 and len(tgt) <= 3:
                return (src.lower(), tgt.lower())
    return None


def load_corpus_entries(
    path: Path, *, base_dir: Path | None = None
) -> tuple[list[EntryRecord], str | None]:
    """Load entries from a corpus JSON file, tolerating schema drift.

    Accepts the canonical ``Corpus`` schema, ``{"dataset": ...,
    "entries": [...]}`` wrappers, and plain entry lists. Entries must
    have non-empty string ``source`` and ``reference`` fields to be
    included; anything else is skipped silently (the caller gets a
    count via the returned list length vs the file's claim, and a
    file-level skip reason when the whole file is unusable).

    Args:
        path: Corpus JSON file path.
        base_dir: If given, corpus display names are paths relative to
            this directory (keeps report names short and unambiguous
            when the same filename exists in multiple dataset trees).

    Returns:
        ``(records, skip_reason)``. ``skip_reason`` is None when the
        file produced at least one record, otherwise a short
        explanation of why the file contributed nothing.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"unreadable: {exc}"

    if isinstance(data, list):
        raw_entries: list[Any] = data
        meta: dict[str, Any] = {}
    elif isinstance(data, dict):
        raw_entries = data.get("entries", [])
        meta = data
    else:
        return [], "top-level JSON is neither an object nor a list"

    if not isinstance(raw_entries, list) or not raw_entries:
        return [], "no 'entries' list found"

    corpus_name = str(path.relative_to(base_dir)) if base_dir else str(path)
    file_segment = infer_file_segment(path, meta)
    lang_pair = _extract_language_pair(meta)

    records: list[EntryRecord] = []
    for index, raw in enumerate(raw_entries):
        if not isinstance(raw, dict):
            continue
        source = raw.get("source")
        reference = raw.get("reference")
        if not isinstance(source, str) or not isinstance(reference, str):
            continue
        if not normalize_text(source):
            # Source is only whitespace/punctuation; fingerprinting it
            # would create meaningless collisions.
            continue

        entry_segment = file_segment
        raw_segment = raw.get("segment")
        if isinstance(raw_segment, str) and raw_segment.strip():
            entry_segment = canonical_segment(raw_segment)

        entry_id = raw.get("id")
        records.append(EntryRecord(
            corpus=corpus_name,
            segment=entry_segment,
            entry_id=str(entry_id) if entry_id is not None else f"index:{index}",
            pair_fp=pair_fingerprint(source, reference),
            source_fp=source_fingerprint(source),
            lang_pair=lang_pair,
        ))

    if not records:
        return [], "no entries with usable source/reference fields"
    return records, None


def _expand_paths(paths: Iterable[str | Path]) -> list[Path]:
    """Expand a mix of files, directories, and glob patterns into a
    sorted, de-duplicated list of JSON file paths. Directories are
    searched recursively for ``*.json``.
    """
    found: set[Path] = set()
    for raw in paths:
        text = str(raw)
        candidates: list[Path]
        if any(ch in text for ch in "*?["):
            candidates = [Path(p) for p in _glob.glob(text, recursive=True)]
        else:
            candidates = [Path(text)]
        for candidate in candidates:
            if candidate.is_dir():
                found.update(candidate.rglob("*.json"))
            elif candidate.is_file():
                found.add(candidate)
    return sorted(found)


# ---------------------------------------------------------------------------
# Overlap detection
# ---------------------------------------------------------------------------

def _assign_severity(
    a: EntryRecord, b: EntryRecord, kind: str
) -> tuple[str, str | None]:
    """Severity for one overlapping entry pair, plus an optional note.

    See module docstring for the severity model. The one refinement
    here: a *source-only* overlap between corpora with known,
    *different* target languages is downgraded to INFO — the same
    English sentence appearing in eng→hau and eng→cym dev sets is
    expected and harmless, and would otherwise drown the report.

    Args:
        a: One side of the overlap.
        b: The other side.
        kind: ``"exact_pair"`` or ``"source_only"``.

    Returns:
        ``(severity, note_or_None)``.
    """
    if (
        kind == "source_only"
        and a.lang_pair is not None
        and b.lang_pair is not None
        and a.lang_pair != b.lang_pair
    ):
        return SEVERITY_INFO, (
            "source-only overlap between different language pairs "
            f"({'-'.join(a.lang_pair)} vs {'-'.join(b.lang_pair)}); "
            "expected for shared pivot-language sources"
        )
    if a.sealed and b.sealed:
        return SEVERITY_WARNING, "both segments are sealed; sealed sets should be disjoint"
    if a.sealed or b.sealed:
        return SEVERITY_CRITICAL, None
    return SEVERITY_INFO, None


@dataclass
class Finding:
    """An aggregated overlap between two (corpus, segment) groups.

    One Finding covers all entry pairs of the same ``kind`` between the
    same two groups, so the report stays readable even when two files
    share hundreds of entries.
    """

    corpus_a: str
    segment_a: str
    corpus_b: str
    segment_b: str
    kind: str           # "exact_pair" | "source_only"
    severity: str
    count: int = 0
    examples: list[tuple[str, str]] = field(default_factory=list)
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "corpus_a": self.corpus_a,
            "segment_a": self.segment_a,
            "corpus_b": self.corpus_b,
            "segment_b": self.segment_b,
            "kind": self.kind,
            "severity": self.severity,
            "count": self.count,
            "examples": [list(pair) for pair in self.examples],
            "note": self.note,
        }


def _ordered(a: EntryRecord, b: EntryRecord) -> tuple[EntryRecord, EntryRecord]:
    """Canonical ordering for a pair: the sealed side first (so
    CRITICAL findings read "sealed × public"), otherwise lexicographic
    by (corpus, segment) so the same two groups always aggregate under
    one key regardless of bucket iteration order.
    """
    if b.sealed and not a.sealed:
        return b, a
    if a.sealed == b.sealed and (b.corpus, b.segment) < (a.corpus, a.segment):
        return b, a
    return a, b


def _collect_overlaps(
    buckets: dict[str, list[EntryRecord]],
    kind: str,
    findings: dict[tuple[str, str, str, str, str, str], Finding],
    *,
    skip_pair: set[tuple[str, str, str, str]] | None = None,
) -> None:
    """Walk fingerprint buckets and aggregate cross-group overlaps.

    Args:
        buckets: fingerprint → entries sharing it.
        kind: ``"exact_pair"`` or ``"source_only"``.
        findings: Aggregation dict, mutated in place.
        skip_pair: For source-only collection, the set of
            ``(corpus_a, id_a, corpus_b, id_b)`` entry pairs already
            reported as exact-pair matches — those are not *additional*
            source-only leakage, just the same duplicate seen twice.
    """
    for bucket in buckets.values():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                first, second = _ordered(bucket[i], bucket[j])
                # Overlaps only matter across groups: two entries in
                # the same corpus AND same segment are an intra-set
                # duplicate, which is a data-quality issue but not
                # contamination between sets.
                if (first.corpus, first.segment) == (second.corpus, second.segment):
                    continue
                pair_key = (first.corpus, first.entry_id,
                            second.corpus, second.entry_id)
                if skip_pair is not None and pair_key in skip_pair:
                    continue
                severity, note = _assign_severity(first, second, kind)
                key = (first.corpus, first.segment,
                       second.corpus, second.segment, kind, severity)
                finding = findings.get(key)
                if finding is None:
                    finding = Finding(
                        corpus_a=first.corpus, segment_a=first.segment,
                        corpus_b=second.corpus, segment_b=second.segment,
                        kind=kind, severity=severity, note=note,
                    )
                    findings[key] = finding
                finding.count += 1
                if len(finding.examples) < MAX_EXAMPLES:
                    finding.examples.append((first.entry_id, second.entry_id))


def check_corpora(
    paths: Iterable[str | Path], *, base_dir: Path | None = None
) -> dict[str, Any]:
    """Check a set of corpus files for cross-set contamination.

    Args:
        paths: Files, directories, or glob patterns. Directories are
            searched recursively for ``*.json``.
        base_dir: Optional directory that corpus display names are
            made relative to.

    Returns:
        Report dict with keys:
            - ``generated``: ISO 8601 timestamp.
            - ``files``: list of ``{path, segment, entries}`` for every
              file that contributed entries.
            - ``skipped``: list of ``{path, reason}`` for files that
              contributed nothing.
            - ``total_entries``: number of entries fingerprinted.
            - ``findings``: list of finding dicts (see ``Finding``),
              sorted CRITICAL → WARNING → INFO, then by overlap count
              descending.
            - ``summary``: ``{CRITICAL: n, WARNING: n, INFO: n}``
              counts of *findings* (group-level, not entry pairs).
            - ``verdict``: one-line plain-language verdict.
    """
    files = _expand_paths(paths)

    loaded_files: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    all_records: list[EntryRecord] = []

    for path in files:
        records, skip_reason = load_corpus_entries(path, base_dir=base_dir)
        display = str(path.relative_to(base_dir)) if base_dir else str(path)
        if skip_reason is not None:
            skipped.append({"path": display, "reason": skip_reason})
            continue
        segments = sorted({r.segment for r in records})
        loaded_files.append({
            "path": display,
            "segment": segments[0] if len(segments) == 1 else segments,
            "entries": len(records),
            "quarantined": is_quarantined(display),
        })
        all_records.extend(records)

    pair_buckets: dict[str, list[EntryRecord]] = {}
    source_buckets: dict[str, list[EntryRecord]] = {}
    for record in all_records:
        pair_buckets.setdefault(record.pair_fp, []).append(record)
        source_buckets.setdefault(record.source_fp, []).append(record)

    findings: dict[tuple[str, str, str, str, str, str], Finding] = {}
    _collect_overlaps(pair_buckets, "exact_pair", findings)

    # Entry pairs already matched exactly must not be double-reported
    # as source-only: source-only findings are reserved for
    # same-source-DIFFERENT-reference leakage.
    exact_pairs: set[tuple[str, str, str, str]] = set()
    for bucket in pair_buckets.values():
        if len(bucket) < 2:
            continue
        for i in range(len(bucket)):
            for j in range(i + 1, len(bucket)):
                first, second = _ordered(bucket[i], bucket[j])
                exact_pairs.add((first.corpus, first.entry_id,
                                 second.corpus, second.entry_id))
    _collect_overlaps(source_buckets, "source_only", findings,
                      skip_pair=exact_pairs)

    sorted_findings = sorted(
        findings.values(),
        key=lambda f: (_SEVERITY_ORDER[f.severity], -f.count,
                       f.corpus_a, f.corpus_b),
    )

    summary = {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 0, SEVERITY_INFO: 0}
    for finding in sorted_findings:
        summary[finding.severity] += 1

    if summary[SEVERITY_CRITICAL]:
        critical_pairs = sum(
            f.count for f in sorted_findings
            if f.severity == SEVERITY_CRITICAL
        )
        verdict = (
            f"CONTAMINATION FOUND: {critical_pairs} entry overlap(s) across "
            f"{summary[SEVERITY_CRITICAL]} finding(s) between sealed "
            "(held_out/gold_standard) segments and development/public sets."
        )
    else:
        verdict = "No held-out contamination found."

    # Annotate findings that involve quarantined corpora: the overlap
    # is real and stays in the report, but the file is already
    # documented as contaminated and withdrawn from evaluation use.
    finding_dicts = [f.to_dict() for f in sorted_findings]
    for fd in finding_dicts:
        quarantined_sides = [
            c for c in (fd["corpus_a"], fd["corpus_b"]) if is_quarantined(c)
        ]
        if quarantined_sides:
            q_note = (
                "involves QUARANTINED corpus "
                + " and ".join(f"`{c}`" for c in quarantined_sides)
                + " — documented contamination; the file is withdrawn from "
                  "held-out evaluation (see the quarantine/README.md beside it)"
            )
            fd["note"] = f"{fd['note']}; {q_note}" if fd["note"] else q_note

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "files": loaded_files,
        "skipped": skipped,
        "total_entries": len(all_records),
        "findings": finding_dicts,
        "summary": summary,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def render_markdown(report: dict[str, Any]) -> str:
    """Render a check_corpora() report as markdown.

    Deliberately prints **only** entry ids, corpus names, segments,
    and counts — never sentence text — so the report can be committed
    without leaking sealed content.

    Args:
        report: The dict returned by :func:`check_corpora`.

    Returns:
        Markdown document as a string.
    """
    lines: list[str] = []
    generated = report["generated"][:10]
    summary = report["summary"]

    lines.append("# Test-Set Contamination Report")
    lines.append("")
    lines.append(f"**Generated:** {generated} by "
                 "`corpora_builder.contamination`")
    lines.append("")
    lines.append(f"## Verdict")
    lines.append("")
    lines.append(f"**{report['verdict']}**")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Files checked: {len(report['files'])} "
                 f"({report['total_entries']} entries fingerprinted)")
    if report["skipped"]:
        lines.append(f"- Files skipped: {len(report['skipped'])}")
    quarantined = [f for f in report["files"] if f.get("quarantined")]
    if quarantined:
        lines.append(
            f"- Quarantined files included: {len(quarantined)} — these "
            "sets have *verified* contamination, are withdrawn from "
            "held-out evaluation, and are kept only for historical "
            "reproducibility (see the quarantine/README.md beside each)."
        )
    lines.append("")
    lines.append("| Severity | Findings | Overlapping entry pairs |")
    lines.append("|----------|---------:|------------------------:|")
    for severity in (SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO):
        pairs = sum(f["count"] for f in report["findings"]
                    if f["severity"] == severity)
        lines.append(f"| {severity} | {summary[severity]} | {pairs} |")
    lines.append("")

    detailed = [f for f in report["findings"]
                if f["severity"] != SEVERITY_INFO]
    info_findings = [f for f in report["findings"]
                     if f["severity"] == SEVERITY_INFO]

    if report["findings"]:
        lines.append("## Findings")
        lines.append("")
        lines.append("Entry text is intentionally omitted; only ids and "
                     "corpus names are shown so this report cannot leak "
                     "sealed content.")
        lines.append("")
        for index, finding in enumerate(detailed, start=1):
            kind_label = ("exact source+reference pair"
                          if finding["kind"] == "exact_pair"
                          else "source-only (different references)")
            lines.append(
                f"### {index}. [{finding['severity']}] "
                f"`{finding['corpus_a']}` ({finding['segment_a']}) × "
                f"`{finding['corpus_b']}` ({finding['segment_b']})"
            )
            lines.append("")
            lines.append(f"- Match kind: {kind_label}")
            lines.append(f"- Overlapping entries: {finding['count']}")
            if finding["note"]:
                lines.append(f"- Note: {finding['note']}")
            shown = finding["examples"][:MAX_EXAMPLES]
            example_text = ", ".join(
                f"`{a}`↔`{b}`" for a, b in shown
            )
            suffix = ""
            if finding["count"] > len(shown):
                suffix = f" … and {finding['count'] - len(shown)} more"
            lines.append(f"- Example entry id pairs (a↔b): {example_text}{suffix}")
            lines.append("")

        if info_findings:
            # INFO findings are expected duplication (dev↔dev mirrors,
            # shared pivot-language sources across target languages).
            # A compact table keeps the report focused on what matters
            # without dropping any information.
            lines.append("### INFO findings (compact)")
            lines.append("")
            lines.append("| Corpus A (segment) | Corpus B (segment) "
                         "| Kind | Entries |")
            lines.append("|--------------------|--------------------"
                         "|------|--------:|")
            for finding in info_findings:
                kind = ("exact pair" if finding["kind"] == "exact_pair"
                        else "source only")
                lines.append(
                    f"| `{finding['corpus_a']}` ({finding['segment_a']}) "
                    f"| `{finding['corpus_b']}` ({finding['segment_b']}) "
                    f"| {kind} | {finding['count']} |"
                )
            lines.append("")
    else:
        lines.append("## Findings")
        lines.append("")
        lines.append("No cross-set overlaps detected.")
        lines.append("")

    lines.append("## Files checked")
    lines.append("")
    lines.append("| File | Segment(s) | Entries |")
    lines.append("|------|------------|--------:|")
    for entry in report["files"]:
        segment = entry["segment"]
        if isinstance(segment, list):
            segment = ", ".join(segment)
        if entry.get("quarantined"):
            segment = f"{segment} (QUARANTINED)"
        lines.append(f"| `{entry['path']}` | {segment} | {entry['entries']} |")
    lines.append("")

    if report["skipped"]:
        lines.append("## Files skipped")
        lines.append("")
        for entry in report["skipped"]:
            lines.append(f"- `{entry['path']}` — {entry['reason']}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point for ``python3 -m corpora_builder.contamination``.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code: 0 when no CRITICAL findings, 1 otherwise,
        2 on usage errors (no input files found).
    """
    parser = argparse.ArgumentParser(
        prog="python3 -m corpora_builder.contamination",
        description=(
            "Check evaluation corpora for test-set contamination: "
            "overlap between sealed (held_out/gold_standard) segments "
            "and development/public sets."
        ),
    )
    parser.add_argument(
        "paths", nargs="+",
        help="Corpus JSON files, directories (searched recursively), "
             "or glob patterns.",
    )
    parser.add_argument(
        "--report", metavar="OUT.md", default=None,
        help="Write a markdown report to this path.",
    )
    parser.add_argument(
        "--json", metavar="OUT.json", default=None,
        help="Write the raw report dict as JSON to this path.",
    )
    parser.add_argument(
        "--base-dir", metavar="DIR", default=None,
        help="Make corpus names in the report relative to this directory.",
    )
    args = parser.parse_args(argv)

    base_dir = Path(args.base_dir).resolve() if args.base_dir else None
    paths = args.paths
    if base_dir is not None:
        # Resolve inputs so relative_to() in the loader cannot fail on
        # mixed relative/absolute inputs.
        paths = [str(Path(p).resolve()) if not any(ch in p for ch in "*?[")
                 else p for p in paths]

    report = check_corpora(paths, base_dir=base_dir)

    if not report["files"] and not report["skipped"]:
        print("error: no corpus JSON files found in the given paths",
              file=sys.stderr)
        return 2

    if args.report:
        Path(args.report).write_text(render_markdown(report),
                                     encoding="utf-8")
        print(f"Markdown report written to {args.report}")
    if args.json:
        Path(args.json).write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"JSON report written to {args.json}")

    summary = report["summary"]
    print()
    print(f"  Files checked:  {len(report['files'])} "
          f"({report['total_entries']} entries)")
    print(f"  CRITICAL:       {summary[SEVERITY_CRITICAL]}")
    print(f"  WARNING:        {summary[SEVERITY_WARNING]}")
    print(f"  INFO:           {summary[SEVERITY_INFO]}")
    print()
    print(f"  {report['verdict']}")

    return 1 if summary[SEVERITY_CRITICAL] else 0


if __name__ == "__main__":
    sys.exit(main())
