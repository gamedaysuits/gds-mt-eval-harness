"""
Build all GlobalVoices eval cards.

Downloads GlobalVoices v2018q4 parallel text from OPUS object storage
(Moses format), creates deterministic test splits, and generates eval
card JSON files for every language pair meeting the 100-entry floor.

GlobalVoices is citizen journalism translated by volunteers — CC-BY-4.0
licensed, "news" domain. The data comes from globalvoices.org.

Usage (from arena/scripts/corpora-builder):
    python -m corpora_builder.build_all_globalvoices [--dry-run] [--yes]

OPUS object storage URL pattern:
    https://object.pouta.csc.fi/OPUS-GlobalVoices/v2018q4/moses/{src}-{tgt}.txt.zip

Inside each zip:
    GlobalVoices.{src}-{tgt}.{src}   (source sentences, one per line)
    GlobalVoices.{src}-{tgt}.{tgt}   (target sentences, one per line)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

# The download/parse/split logic and the SSOT code map live in the adapter
# so the harness fetch-on-miss path and this card generator share exactly
# one definition (see corpora_builder/adapters/globalvoices_adapter.py).
from .adapters.globalvoices_adapter import (
    DEFAULT_TEST_SPLIT_N as TEST_SPLIT_N,
    FLOOR_N,
    GLOBALVOICES_LANGS,
    GV_CODE_MAP,
    OPUS_BASE_URL,
    OPUS_VERSION,
    download_pair,
    make_test_split,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    """Walk up from this file to the repository root."""
    return Path(__file__).resolve().parent.parent.parent.parent.parent


def _default_cards_dir() -> Path:
    return _repo_root() / "cli" / "shared" / "corpora-cards"


def _default_cache_dir() -> Path:
    return _repo_root() / "arena" / "datasets" / ".cache" / "globalvoices"


# ---------------------------------------------------------------------------
# Card generation
# ---------------------------------------------------------------------------

def build_card(
    src_iso3: str,
    tgt_iso3: str,
    test_size: int,
    total_size: int,
) -> dict:
    """Build a corpora card dict for a GlobalVoices eval pair."""
    card_id = f"eval-{src_iso3}-{tgt_iso3}-globalvoices-test-v1"
    
    return {
        "id": card_id,
        "type": "eval",
        "name": f"GlobalVoices {src_iso3}→{tgt_iso3} (test)",
        "version": "1.0",
        "description": (
            f"Evaluation corpus derived from GlobalVoices v2018q4 citizen "
            f"journalism parallel text. {test_size} test sentences from a "
            f"total of {total_size} aligned pairs. News/blog domain. "
            f"CC-BY-4.0 licensed."
        ),
        "pair": {
            "source": src_iso3,
            "target": tgt_iso3,
        },
        "dev": {
            "domain": "news",
            "dataFile": f"{card_id}.json",
            "size": test_size,
        },
        "contamination": {
            "level": "HIGH",
            "notes": (
                "GlobalVoices text is freely available online and widely "
                "crawled. Likely present in frontier model training data."
            ),
        },
        "license": {
            "spdx": "CC-BY-4.0",
            "commercial": True,
            "redistribution": True,
            "aiTraining": True,
            "notes": "Global Voices publishes all content under CC-BY-4.0.",
        },
        "source": {
            "publisher": "Global Voices / OPUS",
            "url": "https://opus.nlpl.eu/GlobalVoices/corpus/version/GlobalVoices",
            "paper": None,
            "citation": (
                "Global Voices. https://globalvoices.org/. "
                "OPUS: Tiedemann, J. (2012). Parallel Data, Tools and "
                "Interfaces in OPUS. LREC 2012."
            ),
            "fundedBy": None,
            # Fetch-from-source recipe, inline in source (the canonical
            # corpora-card shape — see corpora-card.schema.json). The
            # globalvoices-parallel adapter reproduces the tail split.
            "repo_url": f"{OPUS_BASE_URL}/",
            "builder": "globalvoices-parallel",
            "sha256": None,
            "recipe": {
                "split": "test",
                "seed": 42,
                "tail_n": TEST_SPLIT_N,
            },
            "license": "CC-BY-4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
        },
        "doNotTrain": True,
        "_provenance": {
            "addedAt": str(date.today()),
            "populatedFrom": f"OPUS GlobalVoices {OPUS_VERSION} via build_all_globalvoices.py",
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build GlobalVoices eval cards from OPUS object storage."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be built without downloading.")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip confirmation prompt.")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit number of pairs to process (0=all).")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
    )
    
    cards_dir = _default_cards_dir()
    cache_dir = _default_cache_dir()
    
    # Enumerate all possible pairs (English-hub — most data is en-X)
    # But also try X-Y pairs between high-resource languages
    pairs_to_try: list[tuple[str, str]] = []
    
    # All en-X pairs first (these will have the most data)
    for lang in GLOBALVOICES_LANGS:
        if lang == "en":
            continue
        pairs_to_try.append(("en", lang))
    
    # Also try all X-Y pairs between non-English languages
    # (GlobalVoices has some cross-lingual pairs)
    for i, src in enumerate(GLOBALVOICES_LANGS):
        for tgt in GLOBALVOICES_LANGS[i+1:]:
            if src == "en" or tgt == "en":
                continue  # Already added above
            pairs_to_try.append((src, tgt))
    
    if args.limit:
        pairs_to_try = pairs_to_try[:args.limit]
    
    print(f"GlobalVoices builder: {len(pairs_to_try)} pairs to probe")
    print(f"Cards dir: {cards_dir}")
    print(f"Cache dir: {cache_dir}")
    print()
    
    if args.dry_run:
        print("[DRY RUN] Would probe and build cards for all pairs.")
        return 0
    
    if not args.yes:
        print("This will download GlobalVoices data from OPUS (CC-BY-4.0).")
        print("Continue? [y/N] ", end="", flush=True)
        if input().strip().lower() != "y":
            print("Aborted.")
            return 1
    
    # Track results
    built = 0
    skipped_existing = 0
    skipped_floor = 0
    skipped_download = 0
    
    for src, tgt in pairs_to_try:
        src_iso3 = GV_CODE_MAP.get(src, src)
        tgt_iso3 = GV_CODE_MAP.get(tgt, tgt)
        card_id = f"eval-{src_iso3}-{tgt_iso3}-globalvoices-test-v1"
        card_path = cards_dir / f"{card_id}.json"
        
        # Skip if card already exists
        if card_path.exists():
            skipped_existing += 1
            continue
        
        # Download the pair
        result = download_pair(src, tgt, cache_dir)
        if result is None:
            skipped_download += 1
            continue
        
        src_lines, tgt_lines = result
        total_size = len(src_lines)
        
        # Check floor
        if total_size < FLOOR_N:
            logger.info("SKIP %s-%s: only %d sentences (floor=%d)", src, tgt, total_size, FLOOR_N)
            skipped_floor += 1
            continue
        
        # Create test split
        test_src, test_tgt = make_test_split(src_lines, tgt_lines)
        test_size = len(test_src)
        
        # Build card
        card = build_card(src_iso3, tgt_iso3, test_size, total_size)
        
        # Write card
        card_path.write_text(json.dumps(card, indent=2, ensure_ascii=False) + "\n")
        built += 1
        
        if built % 25 == 0:
            print(f"  ... built {built} cards so far")
    
    print()
    print(f"Results:")
    print(f"  Built:            {built}")
    print(f"  Skipped existing: {skipped_existing}")
    print(f"  Below floor:      {skipped_floor}")
    print(f"  Download failed:  {skipped_download}")
    print(f"  Total probed:     {len(pairs_to_try)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
