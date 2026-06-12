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


#: builder id (corpora-card source.builder) → build callable.
BUILDERS: dict[str, Callable[..., Path]] = {
    "edtekla": _build_edtekla,
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


#: builder id (registry source_export.builder) → build callable.
REGISTRY_BUILDERS: dict[str, Callable[..., Path]] = {
    "tatoeba-challenge": _build_tatoeba_challenge,
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
