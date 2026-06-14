"""
Corpus Fetch — fetch-from-source resolution for missing corpora.

Champollion does not host third-party corpora in git. A missing corpus
file can instead be rebuilt locally from a pinned upstream source,
described in one of two places:

1. A **corpora card** (``cli/shared/corpora-cards/``) whose ``source``
   block records the upstream repo and builder:

    "source": {
        "repo_url": "https://github.com/EdTeKLA/IndigenousLanguages_Corpora",
        "ref":      "<commit sha>",
        "builder":  "edtekla",
        "sha256":   "<sha256 of the built corpus file>",
        "license":  "CC-BY-NC-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/"
    }

2. A **registry dataset entry** (``arena/datasets/registry.json``) with
   ``access: "fetch-from-source"`` and a ``source_export`` block pinning
   the upstream export URL, its sha256, and the extraction recipe (the
   Tatoeba mesh corpora use this — see
   ``corpora_builder.adapters.tatoeba_challenge_adapter``):

    "source_export": {
        "builder": "tatoeba-challenge",
        "url":     "https://object.pouta.csc.fi/Tatoeba-Challenge-devtest/test-v2023-09-26.tar",
        "sha256":  "<sha256 of the export archive>",
        "recipe":  {"split": "test", "seed": 42, ...},
        "license": "CC-BY-2.0",
        "license_url": "https://creativecommons.org/licenses/by/2.0/"
    }

When the harness is asked to load a corpus whose file is missing, this
module:

    1. Matches the missing path against corpora cards first (matching
       each card's ``dev.dataFile`` / ``test.dataFile``), then against
       registry ``fetch-from-source`` entries (matching ``path``).
    2. Asks the user to confirm the upstream license and download
       (``--yes`` / ``assume_yes`` / ``CI=true`` skip the prompt; a
       non-interactive stdin without those flags is an error, never a
       hang).
    3. Runs the declared builder (from ``arena/scripts/corpora-builder``)
       to download from the upstream source and rebuild the corpus
       deterministically into the gitignored cache
       ``arena/datasets/.cache/``.
    4. Verifies the build against the pinned ``sha256`` when present.

The builders themselves live in the corpora-builder package so that the
download/parse logic has exactly one home.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

_PACKAGE_DIR = Path(__file__).resolve().parent          # mt_eval_harness/
_ARENA_DIR = _PACKAGE_DIR.parent                        # arena/
_MONOREPO_ROOT = _ARENA_DIR.parent                      # Champollion/

#: Gitignored build cache for fetched corpora.
CACHE_DIR = _ARENA_DIR / "datasets" / ".cache"

#: Dataset registry — fetch-from-source entries carry a `source_export`
#: block describing how to rebuild their corpus from the upstream export.
REGISTRY_PATH = _ARENA_DIR / "datasets" / "registry.json"


# ---------------------------------------------------------------------------
# Corpora-cards directory resolution
# ---------------------------------------------------------------------------

def find_corpora_cards_dir() -> Path | None:
    """Auto-detect the corpora cards directory.

    Mirrors ``language_cards._find_cards_dir`` (the established
    resolution style for shared card directories):

        1. Relative to this file: <monorepo>/cli/shared/corpora-cards/
        2. Walk up from CWD checking cli/shared/corpora-cards/ and
           shared/corpora-cards/
        3. npm install fallback under node_modules/champollion/

    Returns None when not found.
    """
    candidate = _MONOREPO_ROOT / "cli" / "shared" / "corpora-cards"
    if candidate.is_dir():
        return candidate

    check = Path.cwd()
    for _ in range(10):
        for sub in [
            check / "cli" / "shared" / "corpora-cards",
            check / "shared" / "corpora-cards",
        ]:
            if sub.is_dir():
                return sub
        check = check.parent

    npm_path = Path.cwd() / "node_modules" / "champollion" / "shared" / "corpora-cards"
    if npm_path.is_dir():
        return npm_path

    return None


# ---------------------------------------------------------------------------
# Card matching
# ---------------------------------------------------------------------------

def _card_data_files(card: dict[str, Any]) -> list[str]:
    """Collect the dataFile paths a card declares (dev and public test)."""
    files = []
    for split in ("dev", "test"):
        block = card.get(split)
        if isinstance(block, dict) and block.get("dataFile"):
            files.append(block["dataFile"])
    return files


def _is_fetchable(card: dict[str, Any]) -> bool:
    """A card is fetchable when its source block declares repo + builder."""
    source = card.get("source")
    return (
        isinstance(source, dict)
        and bool(source.get("repo_url"))
        and bool(source.get("builder"))
    )


def find_card_for_corpus(
    corpus_path: str | Path,
    cards_dir: Path | None = None,
) -> tuple[dict[str, Any], str] | None:
    """Find a fetchable corpora card whose dataFile matches a corpus path.

    Matching is suffix-based: the card's ``dataFile`` is relative to
    ``arena/datasets/`` (e.g. ``curated/eng-crk-dev-v1.json``), while
    callers pass arbitrary absolute/relative paths. A card matches when
    the requested path ends with the dataFile path, or (fallback) shares
    its filename.

    Returns:
        (card, data_file) for the first match, or None.
    """
    cards_dir = cards_dir or find_corpora_cards_dir()
    if cards_dir is None:
        return None

    requested = Path(corpus_path)
    requested_posix = requested.as_posix()

    filename_match: tuple[dict[str, Any], str] | None = None
    for card_file in sorted(cards_dir.glob("*.json")):
        try:
            card = json.loads(card_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping unreadable corpora card %s: %s",
                           card_file, exc)
            continue
        if not _is_fetchable(card):
            continue
        for data_file in _card_data_files(card):
            if requested_posix.endswith(Path(data_file).as_posix()):
                return card, data_file
            if filename_match is None and requested.name == Path(data_file).name:
                filename_match = (card, data_file)

    return filename_match


# ---------------------------------------------------------------------------
# Builder registry
# ---------------------------------------------------------------------------

def _import_corpora_builder() -> None:
    """Make the corpora-builder package importable from the harness.

    The builder lives at ``arena/scripts/corpora-builder`` and is not
    installed as a dependency of the harness; in the monorepo we add it
    to ``sys.path`` on demand.
    """
    builder_root = _ARENA_DIR / "scripts" / "corpora-builder"
    if builder_root.is_dir() and str(builder_root) not in sys.path:
        sys.path.insert(0, str(builder_root))


def _build_edtekla(card: dict[str, Any], dest: Path, *, assume_yes: bool) -> Path:
    """Builder for the 'edtekla' adapter id."""
    _import_corpora_builder()
    from corpora_builder.adapters import edtekla_adapter

    source = card["source"]
    return edtekla_adapter.build_corpus_file(
        dest,
        cache_dir=CACHE_DIR / "edtekla",
        ref=source.get("ref", edtekla_adapter.DEFAULT_REF),
        auto_yes=assume_yes,
    )


def _build_tatoeba_challenge_from_card(
    card: dict[str, Any], dest: Path, *, assume_yes: bool,
) -> Path:
    """Builder for 'tatoeba-challenge' when invoked from a corpora card.

    Corpora cards store the language pair in ``card["pair"]`` and build
    params in ``card["source"]["recipe"]``, whereas registry entries use
    ``entry["language_pair"]`` and ``entry["source_export"]["recipe"]``.
    This wrapper translates between the two shapes so the underlying
    ``tatoeba_challenge_adapter`` can be used in both code paths.
    """
    _import_corpora_builder()
    from corpora_builder.adapters import tatoeba_challenge_adapter

    source = card["source"]
    pair = card["pair"]
    return tatoeba_challenge_adapter.build_corpus_file(
        dest,
        source_lang=pair["source"],
        target_lang=pair["target"],
        cache_dir=CACHE_DIR / "tatoeba-challenge",
        recipe=source.get("recipe"),
        tar_url=source.get("repo_url", tatoeba_challenge_adapter.TEST_TAR_URL),
        tar_sha256=source.get(
            "sha256", tatoeba_challenge_adapter.TEST_TAR_SHA256,
        ),
        auto_yes=assume_yes,
    )


def _build_globalvoices_parallel(
    card: dict[str, Any], dest: Path, *, assume_yes: bool,
) -> Path:
    """Builder for the 'globalvoices-parallel' source.builder id.

    GlobalVoices cards pin the OPUS export base + tail-split recipe inline
    in ``source`` and the pair in ``pair``. The adapter reproduces the
    deterministic tail split; the card's ``dev.size`` is enforced so a
    drifted upstream can't silently serve a different corpus.
    """
    _import_corpora_builder()
    from corpora_builder.adapters import globalvoices_adapter

    pair = card["pair"]
    source = card["source"]
    return globalvoices_adapter.build_corpus_file(
        dest,
        source_lang=pair["source"],
        target_lang=pair["target"],
        cache_dir=CACHE_DIR / "globalvoices",
        recipe=source.get("recipe"),
        expected_size=(card.get("dev") or {}).get("size"),
        auto_yes=assume_yes,
    )


#: builder id (corpora-card source.builder) → build callable.
BUILDERS: dict[str, Callable[..., Path]] = {
    "edtekla": _build_edtekla,
    "tatoeba-challenge": _build_tatoeba_challenge_from_card,
    "globalvoices-parallel": _build_globalvoices_parallel,
}


# ---------------------------------------------------------------------------
# Registry-based fetch-from-source (source_export entries)
# ---------------------------------------------------------------------------

def find_registry_export_for_corpus(
    corpus_path: str | Path,
    registry_path: Path | None = None,
) -> dict[str, Any] | None:
    """Find a fetch-from-source registry entry matching a corpus path.

    Same matching semantics as ``find_card_for_corpus``: the registry's
    ``path`` is relative to ``arena/datasets/`` while callers pass
    arbitrary paths, so an entry matches when the requested path ends
    with it (or, as a fallback, shares its filename).
    """
    registry_path = registry_path or REGISTRY_PATH
    if not Path(registry_path).is_file():
        return None
    try:
        registry = json.loads(
            Path(registry_path).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Cannot read registry %s: %s", registry_path, exc)
        return None

    requested = Path(corpus_path)
    requested_posix = requested.as_posix()

    filename_match: dict[str, Any] | None = None
    for entry in registry.get("datasets", []):
        if (entry.get("access") or "").lower() != "fetch-from-source":
            continue
        export = entry.get("source_export")
        if not isinstance(export, dict) or not export.get("builder"):
            continue
        rel = entry.get("path")
        if not rel:
            continue
        if requested_posix.endswith(Path(rel).as_posix()):
            return entry
        if filename_match is None and requested.name == Path(rel).name:
            filename_match = entry

    return filename_match


def _build_tatoeba_challenge(
    entry: dict[str, Any], dest: Path, *, assume_yes: bool,
) -> Path:
    """Builder for the 'tatoeba-challenge' source_export builder id."""
    _import_corpora_builder()
    from corpora_builder.adapters import tatoeba_challenge_adapter

    export = entry["source_export"]
    lang_pair = entry["language_pair"]
    return tatoeba_challenge_adapter.build_corpus_file(
        dest,
        source_lang=lang_pair["source"],
        target_lang=lang_pair["target"],
        cache_dir=CACHE_DIR / "tatoeba-challenge",
        recipe=export.get("recipe"),
        tar_url=export.get("url", tatoeba_challenge_adapter.TEST_TAR_URL),
        tar_sha256=export.get(
            "sha256", tatoeba_challenge_adapter.TEST_TAR_SHA256,
        ),
        auto_yes=assume_yes,
    )


# ---------------------------------------------------------------------------
# FLORES / NTREX parallel-text builders
# ---------------------------------------------------------------------------
# These handle multiway registry entries generated by expand_multiway_card().
# Each entry has source_codes.source / source_codes.target containing the
# original file-level codes, and a source_export with the repo URL and
# file pattern. The builder clones the repo, reads the aligned sentence
# files, and pairs them into a harness-json corpus file.

def _load_code_bridge() -> dict[str, Any]:
    """Load the SSOT code bridge for reverse-mapping ISO → file codes."""
    bridge_path = _ARENA_DIR.parent / "cli" / "shared" / "code-bridge.json"
    if bridge_path.exists():
        return json.loads(bridge_path.read_text(encoding="utf-8"))
    return {}


def _iso_to_flores_file_code(iso_code: str) -> str:
    """Map a project ISO 639-3 code to a FLORES+ file code.

    FLORES files use {iso639-3}_{script} format. Since the multiway card
    stores ISO codes (script stripped), we need to add the script back.
    The most common script for each language is used.

    For the two special cases where the ISO base differs:
        cmn-Hans → zho_Hans, cmn-Hant → zho_Hant
    """
    # Handle cmn variants explicitly
    if iso_code == "cmn-Hans":
        return "zho_Hans"
    if iso_code == "cmn-Hant":
        return "zho_Hant"
    if iso_code == "cmn":
        return "zho_Hans"  # default to simplified

    # For all other codes, the FLORES file code is {iso}_{default_script}.
    # We use a small lookup for common non-Latin scripts; everything else
    # defaults to Latn.
    _SCRIPT_MAP: dict[str, str] = {
        "amh": "Ethi", "arb": "Arab", "asm": "Beng", "ben": "Beng",
        "bod": "Tibt", "bul": "Cyrl", "ell": "Grek", "guj": "Gujr",
        "heb": "Hebr", "hin": "Deva", "hye": "Armn", "jpn": "Jpan",
        "kan": "Knda", "kas": "Arab", "kat": "Geor", "khm": "Khmr",
        "kor": "Hang", "lao": "Laoo", "mal": "Mlym", "mar": "Deva",
        "mni": "Beng", "mya": "Mymr", "npi": "Deva", "ory": "Orya",
        "pan": "Guru", "pes": "Arab", "prs": "Arab", "pbt": "Arab",
        "rus": "Cyrl", "san": "Deva", "sat": "Olck", "sin": "Sinh",
        "snd": "Arab", "srp": "Cyrl", "tam": "Taml", "tel": "Telu",
        "tha": "Thai", "tir": "Ethi", "uig": "Arab", "ukr": "Cyrl",
        "urd": "Arab", "ydd": "Hebr", "yue": "Hant",
        # Additional scripts for multi-script languages
        "acm": "Arab", "acq": "Arab", "aeb": "Arab", "ajp": "Arab",
        "apc": "Arab", "ars": "Arab", "ary": "Arab", "arz": "Arab",
        "azb": "Arab", "bak": "Cyrl", "bel": "Cyrl", "bho": "Deva",
        "ckb": "Arab", "crh": "Latn", "dzo": "Tibt", "fuv": "Latn",
        "gaz": "Latn", "grn": "Latn", "hne": "Deva", "khk": "Cyrl",
        "kir": "Cyrl", "kmr": "Latn", "knc": "Arab", "mag": "Deva",
        "mai": "Deva", "mkd": "Cyrl", "awa": "Deva", "nus": "Latn",
        "plt": "Latn", "shn": "Mymr", "tat": "Cyrl", "tgk": "Cyrl",
        "tuk": "Latn", "uzb": "Latn",
    }
    script = _SCRIPT_MAP.get(iso_code, "Latn")
    return f"{iso_code}_{script}"


def _iso_to_ntrex_file_code(iso_code: str) -> str:
    """Map a project ISO 639-3 code to an NTREX repo filename code.

    NTREX uses macrolanguage codes in some filenames. The code bridge's
    ntrex_reverse section handles the mapping.
    """
    bridge = _load_code_bridge()
    reverse = bridge.get("ntrex_reverse", {})

    # Handle script variants
    if iso_code in ("cmn-Hans", "cmn-Hant"):
        script_tag = iso_code.split("-")[1]
        return f"zho-{script_tag}"
    if iso_code == "cmn":
        return "zho-Hans"

    return reverse.get(iso_code, iso_code)


def _clone_or_update_repo(url: str, cache_dir: Path) -> Path:
    """Clone a git repo into cache_dir, or pull if already cloned.

    Returns the path to the cloned repo root.
    """
    import subprocess

    # Derive a stable directory name from the URL
    repo_name = url.rstrip("/").rsplit("/", 1)[-1].replace(".git", "")
    repo_dir = cache_dir / repo_name

    if repo_dir.exists() and (repo_dir / ".git").exists():
        # Already cloned — pull latest
        logger.info("Updating existing clone at %s", repo_dir)
        subprocess.run(
            ["git", "-C", str(repo_dir), "pull", "--ff-only"],
            check=False, capture_output=True,
        )
    else:
        # Fresh clone — shallow to save bandwidth
        logger.info("Cloning %s → %s", url, repo_dir)
        repo_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(repo_dir)],
            check=True, capture_output=True,
        )

    return repo_dir


def _build_parallel_text_corpus(
    entry: dict[str, Any],
    dest: Path,
    *,
    assume_yes: bool,
    source_system: str,
) -> Path:
    """Build a harness-json corpus from parallel text files.

    Works for both FLORES+ and NTREX — each has aligned text files
    (one sentence per line) that can be paired by line number.

    Args:
        entry: Registry entry with language_pair, source_export, source_codes.
        dest: Output path for the built corpus file.
        assume_yes: Skip license confirmation.
        source_system: "flores" or "ntrex" — determines code mapping.
    """
    export = entry["source_export"]
    lang_pair = entry["language_pair"]
    src_iso = lang_pair["source"]
    tgt_iso = lang_pair["target"]

    # Map ISO codes back to file-level codes for the source system
    if source_system == "flores":
        src_file_code = _iso_to_flores_file_code(src_iso)
        tgt_file_code = _iso_to_flores_file_code(tgt_iso)
    else:  # ntrex
        src_file_code = _iso_to_ntrex_file_code(src_iso)
        tgt_file_code = _iso_to_ntrex_file_code(tgt_iso)

    # Clone or update the repo
    repo_url = export["url"]
    cache_dir = CACHE_DIR / source_system
    repo_dir = _clone_or_update_repo(repo_url, cache_dir)

    # Locate the parallel text files
    segment = export.get("segment", "devtest")
    file_pattern = export.get("file_pattern", "")

    if source_system == "flores":
        # FLORES: flores200/{segment}/{lang_code}.{segment}
        src_file = repo_dir / "flores200" / segment / f"{src_file_code}.{segment}"
        tgt_file = repo_dir / "flores200" / segment / f"{tgt_file_code}.{segment}"
    else:
        # NTREX: NTREX-128/newstest2019-ref.{lang_code}.txt
        src_file = repo_dir / "NTREX-128" / f"newstest2019-ref.{src_file_code}.txt"
        tgt_file = repo_dir / "NTREX-128" / f"newstest2019-ref.{tgt_file_code}.txt"

    if not src_file.exists():
        raise FileNotFoundError(
            f"Source file not found: {src_file}\n"
            f"  ISO code: {src_iso}, file code: {src_file_code}"
        )
    if not tgt_file.exists():
        raise FileNotFoundError(
            f"Target file not found: {tgt_file}\n"
            f"  ISO code: {tgt_iso}, file code: {tgt_file_code}"
        )

    # Read aligned sentences
    src_lines = src_file.read_text(encoding="utf-8").strip().splitlines()
    tgt_lines = tgt_file.read_text(encoding="utf-8").strip().splitlines()

    if len(src_lines) != len(tgt_lines):
        raise ValueError(
            f"Line count mismatch: {src_file.name} has {len(src_lines)} lines, "
            f"{tgt_file.name} has {len(tgt_lines)} lines"
        )

    # Build harness-json corpus
    entries = []
    for i, (src_text, tgt_text) in enumerate(zip(src_lines, tgt_lines), 1):
        src_text = src_text.strip()
        tgt_text = tgt_text.strip()
        if not src_text or not tgt_text:
            continue
        entries.append({
            "source": src_text,
            "target": tgt_text,
            "id": str(i),
        })

    corpus = {
        "source_lang": src_iso,
        "target_lang": tgt_iso,
        "entry_count": len(entries),
        "domain": "news",
        "source_dataset": f"{source_system}-{segment}",
        "entries": entries,
    }

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(corpus, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info("Built %s corpus: %s → %s (%d entries) at %s",
                source_system.upper(), src_iso, tgt_iso, len(entries), dest)
    return dest


def _build_flores_parallel(
    entry: dict[str, Any], dest: Path, *, assume_yes: bool,
) -> Path:
    """Builder for 'flores-parallel' registry entries."""
    return _build_parallel_text_corpus(
        entry, dest, assume_yes=assume_yes, source_system="flores",
    )


def _build_ntrex_parallel(
    entry: dict[str, Any], dest: Path, *, assume_yes: bool,
) -> Path:
    """Builder for 'ntrex-parallel' registry entries."""
    return _build_parallel_text_corpus(
        entry, dest, assume_yes=assume_yes, source_system="ntrex",
    )


def _build_globalvoices_parallel_entry(
    entry: dict[str, Any], dest: Path, *, assume_yes: bool,
) -> Path:
    """Builder for 'globalvoices-parallel' registry source_export entries.

    The registry path — used when no corpora card is present, e.g. a third
    party running the harness from the public mirror (which ships the
    registry but not the cli/ corpora cards). The registry entry carries the
    pair, the OPUS export URL, and the tail-split recipe, so the adapter has
    everything it needs without a card.
    """
    _import_corpora_builder()
    from corpora_builder.adapters import globalvoices_adapter

    export = entry["source_export"]
    lang_pair = entry["language_pair"]
    return globalvoices_adapter.build_corpus_file(
        dest,
        source_lang=lang_pair["source"],
        target_lang=lang_pair["target"],
        cache_dir=CACHE_DIR / "globalvoices",
        recipe=export.get("recipe"),
        expected_size=entry.get("size"),
        auto_yes=assume_yes,
    )


#: builder id (registry source_export.builder) → build callable.
#: These let the harness fetch from the registry alone — no corpora card
#: required — which is what makes a standalone install (just the registry +
#: this package) able to auto-download corpora.
REGISTRY_BUILDERS: dict[str, Callable[..., Path]] = {
    "tatoeba-challenge": _build_tatoeba_challenge,
    "flores-parallel": _build_flores_parallel,
    "ntrex-parallel": _build_ntrex_parallel,
    "globalvoices-parallel": _build_globalvoices_parallel_entry,
}


# ---------------------------------------------------------------------------
# Fetch orchestration
# ---------------------------------------------------------------------------

def _non_interactive() -> bool:
    """True when we must not prompt (CI or stdin is not a TTY)."""
    if os.environ.get("CI", "").lower() in ("1", "true", "yes"):
        return True
    try:
        return not sys.stdin.isatty()
    except (AttributeError, ValueError):
        return True


def _confirm_fetch(card: dict[str, Any], *, assume_yes: bool) -> bool:
    """Ask the user to confirm the fetch+build (license acceptance).

    With ``assume_yes`` (--yes flag) or CI=true the prompt is skipped
    and the fetch proceeds. In any other non-interactive context we
    refuse rather than hang on input().
    """
    source = card["source"]
    print()
    print(f"  Corpus '{card.get('id', '?')}' is not present locally.")
    print(f"  It can be fetched from source and built into the local cache:")
    print(f"    Repo:    {source['repo_url']} (ref: {source.get('ref', 'HEAD')})")
    print(f"    License: {source.get('license', 'see card')} "
          f"({source.get('license_url', '')})")
    print(f"    Builder: {source['builder']}")
    print()
    print("  You are responsible for complying with this license.")

    if assume_yes or any(
        os.environ.get(var, "").lower() in ("1", "true", "yes")
        for var in ("CI", "MT_EVAL_AUTO_SETUP")
    ):
        print("  --yes/CI/MT_EVAL_AUTO_SETUP set, proceeding automatically.")
        return True

    if _non_interactive():
        raise RuntimeError(
            f"Corpus for card '{card.get('id', '?')}' must be fetched from "
            f"{source['repo_url']}, but this is a non-interactive session. "
            f"Re-run with --yes to accept the {source.get('license', '')} "
            f"license terms and fetch automatically."
        )

    try:
        answer = input("  Fetch and build now? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return False
    return answer in ("y", "yes")


def _verify_sha256(built: Path, expected: str | None, card_id: str) -> None:
    """Verify a built corpus against the card's pinned hash."""
    if not expected:
        logger.info("No sha256 pinned for '%s' — skipping verification", card_id)
        return
    actual = hashlib.sha256(built.read_bytes()).hexdigest()
    if actual != expected:
        built_path = str(built)
        built.unlink(missing_ok=True)
        raise ValueError(
            f"SHA-256 mismatch for corpus built from card '{card_id}':\n"
            f"  Expected: {expected}\n"
            f"  Got:      {actual}\n"
            f"  The built file ({built_path}) was deleted. The upstream "
            f"repo may have changed since the card's ref/sha256 were "
            f"pinned — re-verify the card's source block."
        )
    logger.info("SHA-256 verified for '%s'", card_id)


def _confirm_fetch_export(
    entry: dict[str, Any], *, assume_yes: bool,
) -> bool:
    """License confirmation for a registry source_export fetch.

    Same gating rules as ``_confirm_fetch``: --yes / CI proceed,
    non-interactive without them raises, otherwise prompt.
    """
    export = entry["source_export"]
    print()
    print(f"  Corpus '{entry.get('id', '?')}' is not present locally.")
    print(f"  It can be fetched from source and built into the local cache:")
    print(f"    Export:  {export.get('url', '?')}")
    print(f"    License: {export.get('license', entry.get('license', 'see registry'))} "
          f"({export.get('license_url', '')})")
    print(f"    Builder: {export['builder']}")
    print()
    print("  You are responsible for complying with this license.")

    if assume_yes or any(
        os.environ.get(var, "").lower() in ("1", "true", "yes")
        for var in ("CI", "MT_EVAL_AUTO_SETUP")
    ):
        print("  --yes/CI/MT_EVAL_AUTO_SETUP set, proceeding automatically.")
        return True

    if _non_interactive():
        raise RuntimeError(
            f"Corpus '{entry.get('id', '?')}' must be fetched from "
            f"{export.get('url', 'its upstream export')}, but this is a "
            f"non-interactive session. Re-run with --yes to accept the "
            f"{export.get('license', '')} license terms and fetch "
            f"automatically."
        )

    try:
        answer = input("  Fetch and build now? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return False
    return answer in ("y", "yes")


def fetch_corpus_from_registry_entry(
    entry: dict[str, Any],
    *,
    assume_yes: bool = False,
) -> Path:
    """Fetch+build the corpus described by a registry source_export block.

    Builds into ``arena/datasets/.cache/<entry path>`` (gitignored) and
    verifies the entry's ``sha256`` when present. Reuses a previously
    built cache file if it passes hash verification.
    """
    export = entry["source_export"]
    builder_id = export["builder"]
    build = REGISTRY_BUILDERS.get(builder_id)
    if build is None:
        raise RuntimeError(
            f"Registry entry '{entry.get('id', '?')}' declares unknown "
            f"source_export builder '{builder_id}'. Known builders: "
            f"{sorted(REGISTRY_BUILDERS)}."
        )

    dest = CACHE_DIR / entry["path"]
    if dest.exists():
        try:
            _verify_sha256(dest, entry.get("sha256"), entry.get("id", "?"))
            logger.info("Using cached built corpus at %s", dest)
            return dest
        except ValueError:
            logger.warning("Cached build failed verification — rebuilding")

    if not _confirm_fetch_export(entry, assume_yes=assume_yes):
        raise RuntimeError(
            f"Fetch declined for registry corpus '{entry.get('id', '?')}'. "
            f"Provide the corpus file locally or re-run and accept the fetch."
        )

    built = build(entry, dest, assume_yes=True)  # license accepted above
    _verify_sha256(built, entry.get("sha256"), entry.get("id", "?"))
    print(f"  Built corpus cached at {built}")
    return built


def fetch_corpus_from_card(
    card: dict[str, Any],
    data_file: str,
    *,
    assume_yes: bool = False,
) -> Path:
    """Fetch+build the corpus described by a card's source block.

    Builds into ``arena/datasets/.cache/<data_file>`` (gitignored) and
    verifies the card's sha256 when present. Reuses a previously built
    cache file if it passes hash verification.

    Raises:
        RuntimeError: Unknown builder, or non-interactive without --yes.
        ConnectionError: Offline / upstream unreachable.
        ValueError: SHA-256 mismatch.
    """
    source = card["source"]
    builder_id = source["builder"]
    build = BUILDERS.get(builder_id)
    if build is None:
        raise RuntimeError(
            f"Corpora card '{card.get('id', '?')}' declares unknown builder "
            f"'{builder_id}'. Known builders: {sorted(BUILDERS)}."
        )

    dest = CACHE_DIR / data_file
    if dest.exists():
        try:
            _verify_sha256(dest, source.get("sha256"), card.get("id", "?"))
            logger.info("Using cached built corpus at %s", dest)
            return dest
        except ValueError:
            logger.warning("Cached build failed verification — rebuilding")

    if not _confirm_fetch(card, assume_yes=assume_yes):
        raise RuntimeError(
            f"Fetch declined for corpus card '{card.get('id', '?')}'. "
            f"Provide the corpus file locally or re-run and accept the fetch."
        )

    built = build(card, dest, assume_yes=True)  # license already accepted above
    _verify_sha256(built, source.get("sha256"), card.get("id", "?"))
    print(f"  Built corpus cached at {built}")
    return built


def try_fetch_missing_corpus(
    corpus_path: str | Path,
    *,
    assume_yes: bool = False,
    cards_dir: Path | None = None,
    registry_path: Path | None = None,
) -> Path | None:
    """Resolve a missing corpus path via fetch-from-source.

    Resolution order: corpora cards first (richer per-corpus metadata),
    then registry ``source_export`` entries. Returns the path to the
    built corpus in the cache, or None when nothing fetchable matches
    (caller should raise its usual FileNotFoundError).
    """
    match = find_card_for_corpus(corpus_path, cards_dir=cards_dir)
    if match is not None:
        card, data_file = match
        return fetch_corpus_from_card(card, data_file, assume_yes=assume_yes)

    entry = find_registry_export_for_corpus(
        corpus_path, registry_path=registry_path,
    )
    if entry is not None:
        return fetch_corpus_from_registry_entry(entry, assume_yes=assume_yes)

    return None
