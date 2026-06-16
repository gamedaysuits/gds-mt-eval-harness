"""
Build evaluation corpora from Tatoeba's REST API.

Uses the TatoebaAPIAdapter to fetch sentence pairs directly — no bulk
downloads, no tars, no disk usage beyond the final corpus JSONs.

Usage:
    cd arena/scripts/corpora-builder
    python3 -m corpora_builder.build_api_corpora
"""

from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from corpora_builder import __version__
from corpora_builder.adapters.tatoeba_api_adapter import TatoebaAPIAdapter
from corpora_builder.cli import _enrich_entry, _filter_by_word_count, _stratified_sample
from corpora_builder.schema import Corpus


# ---------------------------------------------------------------------------
# Pair definitions — "what would someone actually translate to/from?"
#
# Format: (tatoeba_source_code, tatoeba_target_code)
# These codes are Tatoeba-native ISO 639-3 — no mapping needed.
# ---------------------------------------------------------------------------

PAIRS = [
    # === Americas Indigenous ===
    ("spa", "que"),   # Quechua ↔ Spanish (Peru/Bolivia)
    ("spa", "grn"),   # Guaraní ↔ Spanish (Paraguay)
    ("spa", "aym"),   # Aymara ↔ Spanish (Bolivia/Peru)
    ("eng", "haw"),   # Hawaiian ↔ English (US)

    # === Philippines ===
    ("eng", "tgl"),   # Tagalog
    ("eng", "ceb"),   # Cebuano
    ("eng", "ilo"),   # Ilocano
    ("eng", "war"),   # Waray
    ("eng", "hil"),   # Hiligaynon
    ("eng", "pam"),   # Kapampangan
    ("eng", "pag"),   # Pangasinan

    # === Africa ===
    ("eng", "swa"),   # Swahili
    ("eng", "yor"),   # Yoruba
    ("eng", "hau"),   # Hausa (Nigeria)
    ("fra", "hau"),   # Hausa (Niger)
    ("eng", "ibo"),   # Igbo
    ("eng", "zul"),   # Zulu
    ("eng", "xho"),   # Xhosa
    ("fra", "kin"),   # Kinyarwanda (French official)
    ("eng", "kin"),   # Kinyarwanda (English official)
    ("eng", "sna"),   # Shona
    ("eng", "lug"),   # Luganda
    ("eng", "tir"),   # Tigrinya
    ("eng", "amh"),   # Amharic

    # === Celtic / European minority ===
    ("eng", "gle"),   # Irish
    ("eng", "cym"),   # Welsh
    ("spa", "eus"),   # Basque (Spain)
    ("fra", "eus"),   # Basque (France)
    ("spa", "cat"),   # Catalan (Spain)
    ("fra", "cat"),   # Catalan (France)
    ("spa", "glg"),   # Galician
    ("por", "glg"),   # Galician ↔ Portuguese
    ("fra", "ltz"),   # Luxembourgish ↔ French
    ("deu", "ltz"),   # Luxembourgish ↔ German
    ("nld", "fry"),   # West Frisian ↔ Dutch
    ("eng", "mlt"),   # Maltese
    ("ita", "mlt"),   # Maltese ↔ Italian
    ("dan", "fao"),   # Faroese ↔ Danish
    ("eng", "isl"),   # Icelandic
    ("eng", "sme"),   # Northern Sámi

    # === South Asian ===
    ("eng", "hin"),   # Hindi
    ("eng", "ben"),   # Bengali
    ("eng", "tam"),   # Tamil
    ("eng", "tel"),   # Telugu
    ("eng", "kan"),   # Kannada
    ("eng", "mal"),   # Malayalam
    ("eng", "guj"),   # Gujarati
    ("eng", "mar"),   # Marathi
    ("eng", "pan"),   # Punjabi
    ("eng", "sin"),   # Sinhala
    ("eng", "nep"),   # Nepali
    ("hin", "nep"),   # Nepali ↔ Hindi
    ("eng", "urd"),   # Urdu

    # === Southeast Asian ===
    ("eng", "vie"),   # Vietnamese
    ("eng", "tha"),   # Thai
    ("eng", "mya"),   # Burmese
    ("eng", "khm"),   # Khmer
    ("eng", "lao"),   # Lao
    ("eng", "zsm"),   # Malay

    # === East Asian ===
    ("eng", "cmn"),   # Chinese
    ("eng", "jpn"),   # Japanese
    ("eng", "kor"),   # Korean
    ("eng", "mon"),   # Mongolian

    # === Turkic / Central Asian ===
    ("eng", "tur"),   # Turkish
    ("eng", "aze"),   # Azerbaijani
    ("tur", "aze"),   # Azerbaijani ↔ Turkish
    ("eng", "kaz"),   # Kazakh
    ("rus", "kaz"),   # Kazakh ↔ Russian
    ("eng", "uzb"),   # Uzbek
    ("rus", "uzb"),   # Uzbek ↔ Russian
    ("eng", "tuk"),   # Turkmen

    # === Slavic / Baltic / Balkans ===
    ("eng", "rus"),   # Russian
    ("eng", "ukr"),   # Ukrainian
    ("eng", "bel"),   # Belarusian
    ("rus", "bel"),   # Belarusian ↔ Russian
    ("eng", "pol"),   # Polish
    ("eng", "ces"),   # Czech
    ("eng", "slk"),   # Slovak
    ("ces", "slk"),   # Slovak ↔ Czech
    ("eng", "bul"),   # Bulgarian
    ("eng", "srp"),   # Serbian
    ("eng", "bos"),   # Bosnian
    ("eng", "mkd"),   # Macedonian
    ("eng", "sqi"),   # Albanian
    ("eng", "lit"),   # Lithuanian
    ("eng", "lav"),   # Latvian

    # === Germanic / Romance / Major European ===
    ("eng", "deu"),   # German
    ("eng", "fra"),   # French
    ("eng", "spa"),   # Spanish
    ("eng", "ita"),   # Italian
    ("eng", "por"),   # Portuguese
    ("eng", "nld"),   # Dutch
    ("eng", "swe"),   # Swedish
    ("eng", "dan"),   # Danish
    ("eng", "fin"),   # Finnish
    ("eng", "hun"),   # Hungarian
    ("eng", "ron"),   # Romanian
    ("eng", "ell"),   # Greek
    ("eng", "kat"),   # Georgian
    ("eng", "nob"),   # Norwegian Bokmål
    ("eng", "est"),   # Estonian
    ("fin", "est"),   # Estonian ↔ Finnish
    ("eng", "fas"),   # Persian
    ("eng", "heb"),   # Hebrew
    ("eng", "ara"),   # Arabic
]


# ---------------------------------------------------------------------------
# Build logic
# ---------------------------------------------------------------------------

MIN_VIABLE_ENTRIES = 30
MAX_ENTRIES = 200


def build_single_corpus(
    adapter: TatoebaAPIAdapter,
    source_lang: str,
    target_lang: str,
    output_dir: Path,
    seed: int = 42,
) -> dict | None:
    """Build one corpus from the API adapter.

    Fetches → filters → enriches → samples → writes JSON.
    Returns a registry entry dict, or None if too few entries.
    """
    rng = random.Random(seed)

    # Fetch from API (request 300 to have room for filtering)
    raw_entries = adapter.fetch(source_lang, target_lang, max_pairs=300)

    if len(raw_entries) < MIN_VIABLE_ENTRIES:
        return None

    # Filter by word count (3-50 words)
    filtered = _filter_by_word_count(raw_entries, 3, 50)
    if len(filtered) < MIN_VIABLE_ENTRIES:
        return None

    # Enrich (domain + difficulty + register)
    enriched = []
    for raw in filtered:
        try:
            enriched.append(_enrich_entry(raw, adapter.name))
        except ValueError:
            continue

    if len(enriched) < MIN_VIABLE_ENTRIES:
        return None

    # Stratified sampling
    sampled = _stratified_sample(enriched, MAX_ENTRIES, rng)

    # Build corpus
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
            "seed": seed,
            "min_words": 3,
            "max_words": 50,
            "license": "CC-BY-2.0",
            "source_url": "https://tatoeba.org",
        },
    )

    # Write
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
            f"Auto-built via Tatoeba API by corpora-builder v{__version__}. "
            f"{len(sampled)} entries, "
            f"stratified across {len(unique_domains)} domain(s)."
        ),
    }


def update_registry(registry_path: Path, new_entries: list[dict]) -> None:
    """Update the corpus registry with newly built corpora."""
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    else:
        registry = {"registry_version": "1.0.0", "datasets": []}

    existing_by_id = {e["id"]: i for i, e in enumerate(registry["datasets"])}

    for entry in new_entries:
        if entry["id"] in existing_by_id:
            registry["datasets"][existing_by_id[entry["id"]]] = entry
        else:
            registry["datasets"].append(entry)

    registry_path.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  Registry updated: {registry_path} ({len(registry['datasets'])} entries)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    OUTPUT_DIR = Path("/Users/gamedaysuits/local projects/Champollion/arena/datasets/curated")
    REGISTRY = Path("/Users/gamedaysuits/local projects/Champollion/arena/datasets/registry.json")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    adapter = TatoebaAPIAdapter()

    print(f"=== BUILDING {len(PAIRS)} CORPORA VIA TATOEBA API ===")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  Max entries per corpus: {MAX_ENTRIES}")
    print(f"  Min viable entries: {MIN_VIABLE_ENTRIES}")
    print()

    built = []
    skipped = []
    failed = []

    for i, (src, trg) in enumerate(PAIRS, 1):
        label = f"{src}→{trg}"
        print(f"[{i}/{len(PAIRS)}] {label}", end=" ", flush=True)

        try:
            result = build_single_corpus(adapter, src, trg, OUTPUT_DIR)
            if result:
                built.append(result)
                print(f"✅ {result['size']} entries")
            else:
                skipped.append(label)
                print(f"⏭️  <{MIN_VIABLE_ENTRIES} entries")
        except Exception as e:
            failed.append((label, str(e)))
            print(f"❌ {e}")

        sys.stdout.flush()

    # Update registry
    if built:
        update_registry(REGISTRY, built)

    # Summary
    print(f"\n{'=' * 50}")
    print(f"DONE: {len(built)} built, {len(skipped)} skipped, {len(failed)} failed")
    print(f"{'=' * 50}")
    if skipped:
        print(f"Skipped (too few entries): {', '.join(skipped)}")
    if failed:
        print("Failed:")
        for label, err in failed:
            print(f"  {label}: {err}")

    # Disk usage
    total_bytes = sum(f.stat().st_size for f in OUTPUT_DIR.glob("*.json"))
    print(f"\nTotal disk: {total_bytes / (1024*1024):.1f} MB")


if __name__ == "__main__":
    main()
