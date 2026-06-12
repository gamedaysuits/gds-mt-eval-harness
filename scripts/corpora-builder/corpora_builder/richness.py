"""
Corpus richness — language-aware effective length for bridge health.

A benchmark edge is only as real as its entries: 62 single-word
vocabulary items are not a translation bridge. But "words" is the wrong
unit twice over — Japanese and Mandarin write sentences without spaces
(naive count: 1 word), and polysynthetic languages like Plains Cree
pack a sentence into one long word. The unit that works is measured
from the parallel data we already hold:

    character economy  c(L) = median chars on L's side per English
                              word on the aligned side
    effective length   L_eff(text) = chars(text) / c(L)

c(L) is computed from every eng-paired corpus in the registry (7,400+
aligned entries at ship time: cmn 1.6, jpn 2.3, kor 2.6 — compact CJK
scripts; eng baseline 5.0; deu 6.0, zsm 6.8; crk 4.7 — long Cree words
priced by the content they carry). No typology lookup tables; the
estimate sharpens automatically as corpora grow. Languages without
eng-paired data fall back to the global default economy.

The backfill CLI stamps every registry dataset whose corpus file is
locally available with a ``richness`` block::

    "richness": {
      "mean_source_chars": 44.0,
      "mean_effective_words": 8.8,     # chars / c(source language)
      "economy": 5.0,                  # the c(L) used
      "economy_basis": "measured" | "default",
      "computed_from": "eng-fao-dev-v1.json",
      "computed_at": "2026-06-13"
    }

Registry metadata only — corpus bytes are untouched, so fetch-from-
source sha pins stay valid. The queue generator (ecv-v3) reads
``mean_effective_words`` for the reliability factor f_rich; thresholds
and literature anchors live in the public queue-construction spec.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

#: Default chars-per-effective-word when a language has no measured
#: economy (matches the measured English baseline).
DEFAULT_ECONOMY = 5.0

#: Minimum aligned entries before a measured economy is trusted.
MIN_ECONOMY_SAMPLES = 30


def _load_corpus(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _entry_sides(corpus: dict) -> tuple[str, str]:
    lp = corpus.get("language_pair") or {}
    return lp.get("source", ""), lp.get("target", "")


def measure_economy(corpora: dict[str, dict]) -> dict[str, float]:
    """Measure c(L) for every language with eng-paired corpora.

    Returns {lang: median chars-per-English-word}, including an "eng"
    baseline measured from English source sides.
    """
    samples: dict[str, list[float]] = {}
    eng_samples: list[float] = []
    for corpus in corpora.values():
        src, tgt = _entry_sides(corpus)
        if "eng" not in (src, tgt):
            continue
        other = tgt if src == "eng" else src
        for e in corpus.get("entries", []):
            eng_text = e["source"] if src == "eng" else e["reference"]
            oth_text = e["reference"] if src == "eng" else e["source"]
            eng_words = len(eng_text.split())
            if eng_words == 0:
                continue
            samples.setdefault(other, []).append(
                len(oth_text) / eng_words
            )
            eng_words_chars = len(eng_text) / eng_words
            eng_samples.append(eng_words_chars)
    economy = {
        lang: statistics.median(vals)
        for lang, vals in samples.items()
        if len(vals) >= MIN_ECONOMY_SAMPLES
    }
    if eng_samples:
        economy["eng"] = statistics.median(eng_samples)
    return economy


def corpus_richness(
    corpus: dict,
    economy: dict[str, float],
) -> dict:
    """Richness block for one corpus (source-side effective length)."""
    src, _tgt = _entry_sides(corpus)
    entries = corpus.get("entries", [])
    if not entries:
        return {}
    mean_chars = statistics.mean(len(e["source"]) for e in entries)
    c_lang = economy.get(src)
    basis = "measured"
    if c_lang is None:
        c_lang, basis = DEFAULT_ECONOMY, "default"
    return {
        "mean_source_chars": round(mean_chars, 1),
        "mean_effective_words": round(mean_chars / c_lang, 2),
        "economy": round(c_lang, 2),
        "economy_basis": basis,
    }


def find_corpus_file(entry: dict, datasets_dir: Path) -> Path | None:
    rel = entry.get("path")
    if not rel:
        return None
    for base in (datasets_dir, datasets_dir / ".cache"):
        p = base / rel
        if p.is_file():
            return p
    return None


def backfill(registry_path: Path, *, dry_run: bool = False) -> dict:
    """Stamp richness blocks onto every locally-resolvable dataset."""
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    datasets_dir = registry_path.parent

    # Load every resolvable corpus once (economy needs the full set).
    corpora: dict[str, dict] = {}
    file_for: dict[str, Path] = {}
    for ds in registry.get("datasets", []):
        p = find_corpus_file(ds, datasets_dir)
        if p is None:
            continue
        c = _load_corpus(p)
        if c is None or "entries" not in c:
            continue
        if not c.get("language_pair"):
            c["language_pair"] = ds.get("language_pair") or {}
        corpora[ds["id"]] = c
        file_for[ds["id"]] = p

    economy = measure_economy(corpora)
    today = datetime.now(timezone.utc).date().isoformat()

    stamped, skipped = 0, []
    for ds in registry.get("datasets", []):
        c = corpora.get(ds["id"])
        if c is None:
            skipped.append(ds["id"])
            continue
        block = corpus_richness(c, economy)
        if not block:
            skipped.append(ds["id"])
            continue
        block["computed_from"] = file_for[ds["id"]].name
        block["computed_at"] = today
        ds["richness"] = block
        stamped += 1

    if not dry_run:
        registry_path.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return {
        "stamped": stamped,
        "skipped": skipped,
        "economy": {k: round(v, 2) for k, v in sorted(economy.items())},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    result = backfill(Path(args.registry).resolve(), dry_run=args.dry_run)
    print(f"richness stamped on {result['stamped']} datasets"
          + (" (dry run)" if args.dry_run else ""))
    if result["skipped"]:
        print(f"  skipped (no local corpus file): "
              f"{', '.join(result['skipped'][:8])}"
              + (f" … +{len(result['skipped']) - 8}"
                 if len(result['skipped']) > 8 else ""))
    print(f"  measured economies: {len(result['economy'])} languages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
