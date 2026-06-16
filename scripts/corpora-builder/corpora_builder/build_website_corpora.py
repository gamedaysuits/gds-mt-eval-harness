"""
Build dev corpora for the website locale pairs (dogfooding benchmark).

Both Champollion websites (cli/website + arena/website) share the same
13-locale Docusaurus i18n config. This script builds an eng→X Tatoeba
development corpus for each of the 12 non-English locales so the
benchmark sweep can pick the translation method per pair.

Locale → Tatoeba ISO 639-3 mapping (verified against the live API,
2026-06-11):

    fr → fra    de → deu    nl → nld    fil → tgl (closest available)
    es → spa    zh → cmn    ja → jpn    ko  → kor
    pt → por    th → tha    vi → vie    ar  → arb (fetched as ``ara``)

Note on Arabic: Tatoeba's API uses ``ara``, not ``arb``. Querying
``to=arb`` silently drops the target-language filter and returns
translations in every language, which the adapter then discards —
so ``arb`` would always yield zero entries. We therefore FETCH with
``ara`` but NAME the corpus ``eng-arb`` (Tatoeba's Arabic corpus is
MSA, i.e. ISO 639-3 ``arb``): the language-card registry uses ``arb``
(``ara`` is only an alias), and run_baseline_sweep.py resolves the
target language by direct card-filename lookup from the corpus
filename — an ``eng-ara`` corpus would be silently skipped.

Note on Chinese: Tatoeba uses ``cmn`` (Mandarin), not ``zho``.

Reuses the exact build pipeline of build_api_corpora.py (the flow that
produced the existing 48 curated corpora) and writes registry entries
in the same format, including the standard Tatoeba attribution string.

License: all Tatoeba content is CC-BY-2.0. Pass --yes to acknowledge.

Usage:
    cd arena/scripts/corpora-builder
    python3 -m corpora_builder.build_website_corpora --yes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from corpora_builder import USER_AGENT
from corpora_builder.adapters.tatoeba_api_adapter import TatoebaAPIAdapter
from corpora_builder.build_api_corpora import update_registry
from corpora_builder.licensing import LicenseInfo, confirm_batch_download

# Website locale → Tatoeba code. See module docstring for rationale.
WEBSITE_PAIRS = [
    ("eng", "fra"),  # fr
    ("eng", "deu"),  # de
    ("eng", "nld"),  # nl
    ("eng", "tgl"),  # fil (Tagalog is the closest Tatoeba code)
    ("eng", "spa"),  # es
    ("eng", "cmn"),  # zh (Mandarin)
    ("eng", "jpn"),  # ja
    ("eng", "kor"),  # ko
    ("eng", "por"),  # pt
    ("eng", "tha"),  # th
    ("eng", "vie"),  # vi
    ("eng", "arb"),  # ar — corpus named arb (MSA), fetched via Tatoeba code ara
]

# Corpus code → Tatoeba API code, for the few cases where they differ.
TATOEBA_CODE_MAP = {"arb": "ara"}


class WebsiteTatoebaAdapter(TatoebaAPIAdapter):
    """TatoebaAPIAdapter tuned for high-resource website pairs.

    Two deviations from the base adapter:

    1. Code remapping — lets us name a corpus with the language-card
       canonical code (arb) while querying Tatoeba with the code it
       actually serves (ara).

    2. Sentence-length + random-order query params. The api_v0/search
       default ordering returns the SHORTEST sentences first; for
       high-resource pairs like eng→fra the first 300 results are all
       1–2 word sentences ("Amen!", "Marvelous."), which the builder's
       3–50-word filter then removes entirely — 0 viable entries. The
       low-resource pairs the base adapter was written for never hit
       this because their result sets are small and varied. We push the
       word-count filter into the API query and request random order
       for domain/length diversity. (Random order means page contents
       can overlap between requests; the base fetch() already
       deduplicates by text pair.)
    """

    def fetch(self, source_lang, target_lang, **kwargs):
        return super().fetch(
            TATOEBA_CODE_MAP.get(source_lang, source_lang),
            TATOEBA_CODE_MAP.get(target_lang, target_lang),
            **kwargs,
        )

    def _fetch_page(self, source_lang, target_lang, page):
        """Same as the base implementation but with length/sort params."""
        import requests as _requests
        from corpora_builder.adapters.base import RawEntry as _RawEntry

        url = "https://tatoeba.org/en/api_v0/search"
        params = {
            "from": source_lang,
            "to": target_lang,
            "page": page,
            # Mirror the builder's word-count filter server-side so the
            # 1000-result API window isn't wasted on one-word sentences.
            "word_count_min": 3,
            "word_count_max": 50,
            # Default sort is shortest-first; random gives diversity.
            "sort": "random",
        }

        try:
            resp = _requests.get(url, params=params, timeout=15,
                                  headers={"User-Agent": USER_AGENT})
            resp.raise_for_status()
        except _requests.RequestException as exc:
            print(f"    ⚠️  API error on page {page}: {exc}")
            return []

        data = resp.json()
        entries = []
        for sentence in data.get("results", []):
            source_text = sentence.get("text", "").strip()
            source_id = str(sentence.get("id", ""))
            if not source_text:
                continue
            target_text, target_id = self._find_translation(sentence, target_lang)
            if not target_text or source_text == target_text:
                continue
            entries.append(_RawEntry(
                source_text=source_text,
                target_text=target_text,
                source_id=source_id,
                metadata={
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "target_sentence_id": target_id,
                    "provenance": self.build_provenance(
                        source_id=source_id,
                        url=f"https://tatoeba.org/en/sentences/show/{source_id}",
                    ),
                },
            ))
        return entries

# Same attribution string as every existing Tatoeba entry in the registry.
TATOEBA_ATTRIBUTION = "Tatoeba (CC-BY-2.0), via Tatoeba Challenge 2023-09-26"

# Resolve repo paths relative to this file: <repo>/arena/scripts/corpora-builder/corpora_builder/
_ARENA_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = _ARENA_DIR / "datasets" / "curated"
REGISTRY = _ARENA_DIR / "datasets" / "registry.json"


MIN_VIABLE_ENTRIES = 30
MAX_ENTRIES = 200
# High-resource pairs have plenty of data; use the full API window
# (1000 results = 100 pages) so stratified groups actually fill their
# quotas. The base builder's 300 was tuned for low-resource pairs.
FETCH_PAIRS = 1000


def _build_single_corpus_website(adapter, source_lang, target_lang, output_dir, seed=42):
    """build_api_corpora.build_single_corpus with two website-pair tweaks.

    1. Fetches the full 1000-result API window (vs 300) — high-resource
       pairs have the data, and bigger groups fill stratification quotas.
    2. Tops the stratified sample up to MAX_ENTRIES from the unsampled
       remainder (seeded). The shared ``_stratified_sample`` caps every
       (domain × difficulty) group at ``max_entries / num_groups`` and
       never redistributes unused quota, so dominant-domain corpora land
       at ~65 entries no matter how much data exists. Stratification
       still happens first, so balance is preserved; the top-up only
       fills otherwise-wasted quota. (The existing 48 corpora range
       35–196 entries for the same reason; we keep their format.)
    """
    import random
    from collections import Counter
    from datetime import datetime, timezone

    from corpora_builder import __version__
    from corpora_builder.cli import _enrich_entry, _filter_by_word_count, _stratified_sample
    from corpora_builder.schema import Corpus

    rng = random.Random(seed)

    raw_entries = adapter.fetch(source_lang, target_lang, max_pairs=FETCH_PAIRS)
    if len(raw_entries) < MIN_VIABLE_ENTRIES:
        return None

    filtered = _filter_by_word_count(raw_entries, 3, 50)
    if len(filtered) < MIN_VIABLE_ENTRIES:
        return None

    enriched = []
    for raw in filtered:
        try:
            enriched.append(_enrich_entry(raw, adapter.name))
        except ValueError:
            continue
    if len(enriched) < MIN_VIABLE_ENTRIES:
        return None

    sampled = _stratified_sample(enriched, MAX_ENTRIES, rng)

    # Top up to MAX_ENTRIES from the unsampled remainder (seeded shuffle).
    if len(sampled) < MAX_ENTRIES:
        sampled_ids = {id(e) for e in sampled}
        leftovers = [e for e in enriched if id(e) not in sampled_ids]
        rng.shuffle(leftovers)
        sampled = sampled + leftovers[: MAX_ENTRIES - len(sampled)]

    unique_domains = sorted(set(entry.domain for entry in sampled))
    now_utc = datetime.now(timezone.utc).isoformat()
    corpus_id = f"tatoeba-{source_lang}-{target_lang}-dev"

    corpus = Corpus(
        corpus_id=corpus_id,
        version=__version__,
        language_pair={"source": source_lang, "target": target_lang},
        segment="development",
        created=now_utc,
        entry_count=len(sampled),
        domains=unique_domains,
        entries=sampled,
        provenance={
            "builder": "champollion-corpora-builder",
            "builder_version": __version__,
            "source_adapter": "tatoeba-api",
            "builder_module": "build_website_corpora",
            "seed": seed,
            "min_words": 3,
            "max_words": 50,
            "fetch_window": FETCH_PAIRS,
            "sampling": "stratified + seeded top-up to max_entries",
            "license": "CC-BY-2.0",
            "source_url": "https://tatoeba.org",
        },
    )

    filename = f"{source_lang}-{target_lang}-dev-v1.json"
    output_path = output_dir / filename
    corpus.to_json(output_path)

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
        "sha256": None,
        "access": "local",
        "do_not_train": True,
        "license": "CC-BY-2.0",
        "source": "Tatoeba (https://tatoeba.org)",
        "path": f"curated/{filename}",
        "segment": "development",
        "notes": (
            f"Auto-built via Tatoeba API by corpora-builder v{__version__} "
            f"(build_website_corpora: 1000-result fetch window, stratified "
            f"sampling with seeded top-up). {len(sampled)} entries, "
            f"stratified across {len(unique_domains)} domain(s)."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build dev corpora for the 12 website locale pairs via the Tatoeba API.",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip license confirmation prompt (CC-BY-2.0 acknowledged).",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip pairs whose corpus JSON already exists (default: on).",
    )
    args = parser.parse_args()

    # License confirmation — same gate as the batch builder.
    batch_license = LicenseInfo(
        source_name="Tatoeba",
        license_id="CC-BY-2.0",
        license_url="https://creativecommons.org/licenses/by/2.0/",
        source_url="https://tatoeba.org",
        download_url="(Tatoeba REST API, paginated)",
    )
    if not confirm_batch_download(batch_license, len(WEBSITE_PAIRS), auto_yes=args.yes):
        print("  Cancelled.")
        sys.exit(0)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    adapter = WebsiteTatoebaAdapter()

    built: list[dict] = []
    skipped: list[str] = []
    failed: list[str] = []

    print(f"=== BUILDING {len(WEBSITE_PAIRS)} WEBSITE-PAIR CORPORA VIA TATOEBA API ===")
    print(f"  Output:   {OUTPUT_DIR}")
    print(f"  Registry: {REGISTRY}")
    print()

    for i, (src, trg) in enumerate(WEBSITE_PAIRS, 1):
        label = f"{src}→{trg}"
        out_file = OUTPUT_DIR / f"{src}-{trg}-dev-v1.json"
        if args.skip_existing and out_file.exists():
            print(f"[{i}/{len(WEBSITE_PAIRS)}] {label} already exists — skipping")
            skipped.append(label)
            continue

        print(f"[{i}/{len(WEBSITE_PAIRS)}] {label}", end=" ", flush=True)
        try:
            result = _build_single_corpus_website(adapter, src, trg, OUTPUT_DIR)
        except Exception as exc:  # network errors shouldn't kill the batch
            print(f"❌ {exc}")
            failed.append(label)
            continue

        if result:
            result["attribution"] = TATOEBA_ATTRIBUTION
            built.append(result)
            print(f"✅ {result['size']} entries")
        else:
            print("⚠️  below minimum viable entries — skipped")
            skipped.append(label)

    if built:
        update_registry(REGISTRY, built)

    print()
    print("=== DONE ===")
    print(f"  Built:   {len(built)}")
    print(f"  Skipped: {len(skipped)} {skipped if skipped else ''}")
    print(f"  Failed:  {len(failed)} {failed if failed else ''}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
