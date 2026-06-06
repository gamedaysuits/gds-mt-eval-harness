"""
Probe Tatoeba for language pair availability.

Checks which language pairs have downloadable data on Tatoeba by
sending HTTP HEAD requests to the known download URL pattern.  Reports
file sizes and estimated entry counts.

Usage:
    python -m corpora_builder.probe_tatoeba --language-cards-dir /path/to/cards
    python -m corpora_builder.probe_tatoeba --langs eng fra deu jpn

Output: a JSON report of all viable pairs (those with data available).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import requests

from corpora_builder.licensing import build_tatoeba_url


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PairProbe:
    """Result of probing a single language pair on Tatoeba."""
    source_lang: str
    target_lang: str
    url: str
    available: bool
    file_size_bytes: int | None = None    # from Content-Length header
    file_size_human: str = ""             # e.g., "4.2 MB"
    error: str | None = None


def _human_size(size_bytes: int) -> str:
    """Convert bytes to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ---------------------------------------------------------------------------
# Probing
# ---------------------------------------------------------------------------

def probe_pair(source_lang: str, target_lang: str) -> PairProbe:
    """Check if a Tatoeba pair file exists and get its size.

    Uses HTTP HEAD to avoid downloading the entire file.  Tatoeba
    returns 200 for existing pairs and 404 for missing ones.

    Args:
        source_lang: ISO 639-3 source language code.
        target_lang: ISO 639-3 target language code.

    Returns:
        PairProbe with availability and size information.
    """
    url = build_tatoeba_url(source_lang, target_lang)

    try:
        resp = requests.head(url, timeout=10, allow_redirects=True)
        if resp.status_code == 200:
            content_length = resp.headers.get("Content-Length")
            size_bytes = int(content_length) if content_length else None
            return PairProbe(
                source_lang=source_lang,
                target_lang=target_lang,
                url=url,
                available=True,
                file_size_bytes=size_bytes,
                file_size_human=_human_size(size_bytes) if size_bytes else "unknown",
            )
        elif resp.status_code == 404:
            return PairProbe(
                source_lang=source_lang,
                target_lang=target_lang,
                url=url,
                available=False,
            )
        else:
            return PairProbe(
                source_lang=source_lang,
                target_lang=target_lang,
                url=url,
                available=False,
                error=f"HTTP {resp.status_code}",
            )
    except requests.RequestException as exc:
        return PairProbe(
            source_lang=source_lang,
            target_lang=target_lang,
            url=url,
            available=False,
            error=str(exc),
        )


def probe_all_pairs(
    language_codes: list[str],
    *,
    delay_seconds: float = 0.2,
    progress: bool = True,
) -> list[PairProbe]:
    """Probe Tatoeba for all combinations of the given language codes.

    Generates all ordered pairs (A→B where A != B) but only probes
    the canonical URL once per unordered pair (since Tatoeba stores
    each pair file once with codes sorted alphabetically).

    Args:
        language_codes: List of ISO 639-3 codes to probe.
        delay_seconds: Delay between requests (be nice to Tatoeba's servers).
        progress: If True, print progress to stdout.

    Returns:
        List of PairProbe results (only viable pairs, i.e., available=True).
    """
    # Deduplicate: Tatoeba stores files as {sorted_a}-{sorted_b}.tsv.bz2
    # so eng-fra and fra-eng are the same file.  We probe each unordered
    # pair once and record both directions as available.
    probed_urls: dict[str, PairProbe] = {}
    viable: list[PairProbe] = []

    # Generate all unordered pairs
    codes = sorted(set(language_codes))
    total_pairs = len(codes) * (len(codes) - 1) // 2
    checked = 0

    for i, lang_a in enumerate(codes):
        for lang_b in codes[i + 1:]:
            checked += 1

            url = build_tatoeba_url(lang_a, lang_b)

            # Skip if already probed (shouldn't happen with sorted iteration)
            if url in probed_urls:
                continue

            if progress:
                print(
                    f"\r  Probing [{checked}/{total_pairs}] "
                    f"{lang_a}-{lang_b}...",
                    end="",
                    flush=True,
                )

            result = probe_pair(lang_a, lang_b)
            probed_urls[url] = result

            if result.available:
                # Record both directions as viable
                viable.append(result)
                # Also record the reverse direction (same file, different pair order)
                reverse = PairProbe(
                    source_lang=lang_b,
                    target_lang=lang_a,
                    url=result.url,
                    available=True,
                    file_size_bytes=result.file_size_bytes,
                    file_size_human=result.file_size_human,
                )
                viable.append(reverse)

            # Be polite to Tatoeba's servers
            time.sleep(delay_seconds)

    if progress:
        print()  # newline after progress

    return viable


# ---------------------------------------------------------------------------
# Language card loading
# ---------------------------------------------------------------------------

# Map from champollion language card filenames (ISO 639-1/3 codes)
# to Tatoeba/ISO 639-3 codes.  Cards use short codes (e.g., "fr.json")
# but Tatoeba uses 3-letter codes (e.g., "fra").
#
# Only entries where the card code DIFFERS from the Tatoeba code
# need to appear here.  3-letter codes like "crk", "moe" pass through.
_CARD_TO_TATOEBA: dict[str, str] = {
    # ISO 639-1 → ISO 639-3
    # Sorted alphabetically by card code
    "am": "amh",
    "ar": "ara",
    "ay": "aym",
    "az": "aze",
    "be": "bel",
    "bg": "bul",
    "bn": "ben",
    "bs": "hbs",       # Bosnian → OPUS uses Serbo-Croatian macro code
    "ca": "cat",
    "cs": "ces",
    "cy": "cym",
    "da": "dan",
    "de": "deu",
    "el": "ell",
    "es": "spa",
    "es-MX": "spa",   # Mexican Spanish → Tatoeba's generic Spanish
    "et": "est",
    "eu": "eus",
    "fa": "fas",
    "fi": "fin",
    "fo": "fao",
    "fr": "fra",
    "fr-CA": "fra",   # Canadian French → Tatoeba's generic French
    "fy": "fry",
    "ga": "gle",
    "gl": "glg",
    "gn": "grn",
    "gu": "guj",
    "ha": "hau",
    "he": "heb",
    "hi": "hin",
    "hu": "hun",
    "id": "ind",
    "ig": "ibo",
    "is": "isl",
    "it": "ita",
    "ja": "jpn",
    "ka": "kat",
    "kk": "kaz",
    "km": "khm",
    "kn": "kan",
    "ko": "kor",
    "lb": "ltz",
    "lg": "lug",
    "lo": "lao",
    "lt": "lit",
    "lv": "lav",
    "mi": "mri",
    "mk": "mkd",
    "ml": "mal",
    "mn": "mon",
    "mr": "mar",
    "ms": "msa",       # Malay → OPUS uses macrolanguage code
    "mt": "mlt",
    "my": "mya",
    "nb": "nor",       # Norwegian Bokmål → OPUS uses macrolanguage code
    "ne": "nep",
    "nl": "nld",
    "pa": "pan",
    "pl": "pol",
    "pt": "por",
    "pt-PT": "por",   # European Portuguese → Tatoeba's generic Portuguese
    "qu": "que",
    "ro": "ron",
    "ru": "rus",
    "rw": "kin",
    "se": "sme",       # Northern Sámi
    "si": "sin",
    "sk": "slk",
    "sn": "sna",
    "sq": "sqi",
    "sr": "hbs",       # Serbian → OPUS uses Serbo-Croatian macro code
    "sv": "swe",
    "sw": "swa",
    "ta": "tam",
    "te": "tel",
    "th": "tha",
    "ti": "tir",
    "tk": "tuk",
    "tl": "tgl",
    "tr": "tur",
    "uk": "ukr",
    "ur": "urd",
    "uz": "uzb",
    "vi": "vie",
    "xh": "xho",
    "yo": "yor",
    "zh": "zho",       # Chinese → OPUS uses macrolanguage code
    "zh-TW": "zho",   # Traditional Chinese → same OPUS macro code
    "zu": "zul",
}


def load_language_codes_from_cards(cards_dir: str | Path) -> list[str]:
    """Extract Tatoeba-compatible language codes from champollion language cards.

    Reads all .json files in the cards directory (excluding genera/
    subdirectories, conlang cards prefixed with 'x-', Klingon, and
    the language-tree.json metadata file) and maps each to a Tatoeba
    language code.

    Args:
        cards_dir: Path to the champollion language-cards directory.

    Returns:
        Deduplicated, sorted list of Tatoeba-compatible language codes.
    """
    cards_path = Path(cards_dir)
    if not cards_path.is_dir():
        raise FileNotFoundError(f"Language cards directory not found: {cards_path}")

    tatoeba_codes: set[str] = set()

    for card_file in sorted(cards_path.glob("*.json")):
        # Skip metadata files and conlang/joke cards
        basename = card_file.stem
        if basename == "language-tree":
            continue
        if basename.startswith("x-"):
            continue
        if basename == "tlh":  # Klingon
            continue

        # Map card code to Tatoeba code
        tatoeba_code = _CARD_TO_TATOEBA.get(basename, basename)
        tatoeba_codes.add(tatoeba_code)

    return sorted(tatoeba_codes)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI entry point for the Tatoeba probe."""
    parser = argparse.ArgumentParser(
        description="Probe Tatoeba for available language pair downloads.",
    )
    parser.add_argument(
        "--language-cards-dir",
        help="Path to champollion language-cards directory. Probes all real languages.",
    )
    parser.add_argument(
        "--langs",
        nargs="+",
        help="Explicit list of ISO 639-3 codes to probe (e.g., eng fra deu).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file path for the probe results.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between HTTP requests in seconds (default: 0.2).",
    )

    args = parser.parse_args()

    # Resolve language codes
    if args.langs:
        codes = args.langs
    elif args.language_cards_dir:
        codes = load_language_codes_from_cards(args.language_cards_dir)
        print(f"  Loaded {len(codes)} language codes from cards: {', '.join(codes)}")
    else:
        print(
            "Error: Provide either --language-cards-dir or --langs.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Probe
    print(f"\n  Probing Tatoeba for all pairs among {len(codes)} languages...")
    total_pairs = len(codes) * (len(codes) - 1) // 2
    print(f"  Total pairs to check: {total_pairs}")
    print()

    viable = probe_all_pairs(codes, delay_seconds=args.delay)

    # Report
    # Deduplicate by canonical URL for the summary (each file serves both directions)
    unique_files = {r.url for r in viable}
    available_pairs = len(viable)

    print(f"\n  Results:")
    print(f"    Unique files available:  {len(unique_files)}")
    print(f"    Language pairs (both directions): {available_pairs}")
    print()

    # Sort by file size (largest first) for display
    by_size = sorted(
        [r for r in viable if r.source_lang < r.target_lang],  # canonical direction only
        key=lambda r: r.file_size_bytes or 0,
        reverse=True,
    )

    # Print top pairs
    print(f"  {'Pair':<12} {'Size':>10}  URL")
    print(f"  {'-'*12} {'-'*10}  {'-'*50}")
    for r in by_size[:30]:  # Show top 30
        pair = f"{r.source_lang}→{r.target_lang}"
        print(f"  {pair:<12} {r.file_size_human:>10}  {r.url}")

    if len(by_size) > 30:
        print(f"  ... and {len(by_size) - 30} more pairs")

    # Write JSON output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "probe_date": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat(),
            "language_codes": codes,
            "total_probed": total_pairs,
            "viable_files": len(unique_files),
            "viable_pairs": available_pairs,
            "pairs": [asdict(r) for r in viable],
        }
        output_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n  Report written to: {output_path}")


if __name__ == "__main__":
    main()
