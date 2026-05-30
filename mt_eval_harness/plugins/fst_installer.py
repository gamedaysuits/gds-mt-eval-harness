"""
FST Installer — Download and install GiellaLT FST transducers.

This module handles the interactive download flow for GiellaLT FSTs.
When an evaluation targets a language with a known FST, and the FST
isn't installed locally, this module:

    1. Identifies the correct GitHub release for the language
    2. Prompts the user for download consent
    3. Downloads the release zip
    4. Extracts .hfstol files to the local cache
    5. Writes provenance metadata

WHY THIS MODULE EXISTS:
    FST validation is the morphological ground truth for polysynthetic
    and low-resource languages. Without it, evals are flying blind —
    chrF++ and BLEU can't tell you if "niwâpamâw" is a valid Cree word.
    By gating evals on FST availability, we ensure quality metrics for
    languages that need them most.

DESIGN DECISIONS:
    - Interactive consent: We never download without asking. The FSTs
      are 5-30MB binaries from third-party repos.
    - Provenance tracking: Every install records version, URL, SHA256,
      and timestamp so we can audit and reproduce.
    - Legacy format only: We handle standalone .hfstol zips (lang-crk
      style). Divvun-packaged FSTs require their own toolchain.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Standard cache directory for all FSTs managed by the harness
# ---------------------------------------------------------------------------

FST_CACHE_ROOT = Path.home() / ".mt-eval" / "fsts"

# ---------------------------------------------------------------------------
# Known GiellaLT FST repositories
#
# This registry maps ISO 639-3 codes to their GiellaLT repo metadata.
# Only languages with standalone FST releases (legacy format) are listed.
# Languages using Divvun packaging are noted but handled differently.
#
# WHY A STATIC REGISTRY:
#   The harness is a standalone Python package — it can't reach into the
#   champollion language cards at runtime. This registry mirrors what the
#   language card's resources.fsts field documents, but is self-contained.
#   The card generator and this registry should stay in sync.
# ---------------------------------------------------------------------------

GIELLALT_FST_REGISTRY: dict[str, dict[str, Any]] = {
    # Languages with standalone FST zip releases (legacy format)
    "crk": {
        "name": "Plains Cree",
        "repo": "giellalt/lang-crk",
        "release_tag": "fst-v2021.7.8",
        "asset_pattern": "plains-cree-fsts-",
        "format": "legacy-zip",
    },
    # Languages with Divvun-packaged FSTs (noted for guidance, not auto-install)
    # These use speller-XXX/vN.N.N tags with .drb or .pkt.tar.zst assets.
    # Users need the Divvun manager to extract .hfstol files from these.
    "sme": {
        "name": "Northern Sámi",
        "repo": "giellalt/lang-sme",
        "format": "divvun",
    },
    "sma": {
        "name": "Southern Sámi",
        "repo": "giellalt/lang-sma",
        "format": "divvun",
    },
    "smj": {
        "name": "Lule Sámi",
        "repo": "giellalt/lang-smj",
        "format": "divvun",
    },
    "smn": {
        "name": "Inari Sámi",
        "repo": "giellalt/lang-smn",
        "format": "divvun",
    },
    "sms": {
        "name": "Skolt Sámi",
        "repo": "giellalt/lang-sms",
        "format": "divvun",
    },
    "fin": {
        "name": "Finnish",
        "repo": "giellalt/lang-fin",
        "format": "divvun",
    },
    "nob": {
        "name": "Norwegian Bokmål",
        "repo": "giellalt/lang-nob",
        "format": "divvun",
    },
    "iku": {
        "name": "Inuktitut",
        "repo": "giellalt/lang-iku",
        "format": "divvun",
    },
}


# ---------------------------------------------------------------------------
# Cache path helpers
# ---------------------------------------------------------------------------

def get_fst_cache_dir(lang_code: str) -> Path:
    """Return the standard cache directory for a language's FST files.

    Checks multiple locations in priority order:
        1. ~/.mt-eval/fsts/{code}/          (harness-managed, preferred)
        2. ~/.crk-translate/models/         (legacy CRK location)
    """
    primary = FST_CACHE_ROOT / lang_code
    if primary.exists() and any(primary.glob("*.hfstol")):
        return primary

    # Legacy CRK fallback — check the old location
    if lang_code == "crk":
        legacy = Path.home() / ".crk-translate" / "models"
        # Check any version subdirectory
        for version_dir in sorted(legacy.glob("fst-v*"), reverse=True):
            if any(version_dir.glob("*.hfstol")):
                return version_dir

    return primary


def find_analyzer_hfstol(fst_dir: Path) -> Path | None:
    """Find the best analyzer .hfstol file in a directory.

    Prefers 'strict' over 'relaxed', 'normative' over other variants.
    Returns None if no analyzer found.
    """
    all_hfstol = list(fst_dir.rglob("*.hfstol"))
    if not all_hfstol:
        return None

    # Filter to analyzers only
    analyzers = [
        f for f in all_hfstol
        if "analy" in f.name.lower()  # matches both "analyzer" and "analyser"
    ]

    if not analyzers:
        # No explicit analyzer — return the first .hfstol as fallback
        return all_hfstol[0]

    # Prefer strict > normative > relaxed > other
    for preference in ["strict", "normative"]:
        for a in analyzers:
            if preference in a.name.lower():
                return a

    # No preference match — return first analyzer
    return analyzers[0]


def is_fst_installed(lang_code: str) -> bool:
    """Check if an FST is installed for the given language code."""
    fst_dir = get_fst_cache_dir(lang_code)
    return fst_dir.exists() and find_analyzer_hfstol(fst_dir) is not None


# ---------------------------------------------------------------------------
# Download and install
# ---------------------------------------------------------------------------

def _download_legacy_zip(repo: str, tag: str, asset_pattern: str) -> bytes:
    """Download a legacy-format FST zip from GitHub Releases.

    Uses stdlib urllib (no external dependencies) to:
    1. Query the GitHub API for the release metadata
    2. Find the matching zip asset
    3. Download the zip content

    Args:
        repo: GitHub repo (e.g. "giellalt/lang-crk")
        tag: Release tag (e.g. "fst-v2021.7.8")
        asset_pattern: Prefix to match in asset names

    Returns:
        Raw zip bytes

    Raises:
        RuntimeError: If download fails
    """
    import urllib.request
    import urllib.error

    # Use GitHub API to find the asset URL
    api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    req = urllib.request.Request(
        api_url,
        headers={"Accept": "application/vnd.github.v3+json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            release = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"GitHub API returned {e.code} for {api_url}"
        )

    assets = release.get("assets", [])

    # Find the zip asset matching the pattern
    zip_asset = None
    for asset in assets:
        name = asset["name"]
        if name.endswith(".zip") and asset_pattern in name:
            zip_asset = asset
            break

    if zip_asset is None:
        available = [a["name"] for a in assets]
        raise RuntimeError(
            f"No zip asset matching '{asset_pattern}' in release {tag}. "
            f"Available: {available}"
        )

    # Download the zip
    download_url = zip_asset["browser_download_url"]
    size_mb = zip_asset["size"] / 1024 / 1024
    print(f"  Downloading {zip_asset['name']} ({size_mb:.1f} MB)...")

    with urllib.request.urlopen(download_url, timeout=120) as dl_resp:
        content = dl_resp.read()

    print(f"  Downloaded {len(content) / 1024 / 1024:.1f} MB")
    return content


def install_fst(lang_code: str) -> Path:
    """Download and install the FST for a language.

    Looks up the language in GIELLALT_FST_REGISTRY, downloads the
    release zip, extracts .hfstol files, and writes provenance metadata.

    Args:
        lang_code: ISO 639-3 language code (e.g. "crk")

    Returns:
        Path to the installed FST cache directory

    Raises:
        RuntimeError: If download or extraction fails
        KeyError: If language not in registry
    """
    if lang_code not in GIELLALT_FST_REGISTRY:
        raise KeyError(f"No GiellaLT FST registered for '{lang_code}'")

    entry = GIELLALT_FST_REGISTRY[lang_code]

    if entry["format"] != "legacy-zip":
        raise RuntimeError(
            f"FST for {entry['name']} uses Divvun packaging, which requires "
            f"the Divvun manager. Install from: https://divvun.no/"
        )

    # Download the zip
    content = _download_legacy_zip(
        repo=entry["repo"],
        tag=entry["release_tag"],
        asset_pattern=entry["asset_pattern"],
    )

    # Calculate SHA256 for provenance
    sha256 = hashlib.sha256(content).hexdigest()

    # Extract to cache directory
    install_dir = FST_CACHE_ROOT / lang_code
    install_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        hfstol_count = 0
        for name in zf.namelist():
            if name.endswith(".hfstol"):
                # Extract to flat directory (ignore zip subdirectories)
                target = install_dir / Path(name).name
                target.write_bytes(zf.read(name))
                hfstol_count += 1
                print(f"  Extracted: {Path(name).name}")

        if hfstol_count == 0:
            raise RuntimeError(
                f"No .hfstol files found in zip. Contents: {zf.namelist()}"
            )

    # Write provenance metadata
    provenance = {
        "lang_code": lang_code,
        "repo": entry["repo"],
        "release_tag": entry["release_tag"],
        "sha256": sha256,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "hfstol_files": [f.name for f in install_dir.glob("*.hfstol")],
    }
    provenance_path = install_dir / "provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2))
    print(f"  Provenance: {provenance_path}")

    return install_dir


# ---------------------------------------------------------------------------
# Interactive consent flow
# ---------------------------------------------------------------------------

def prompt_fst_install(lang_code: str, lang_name: str) -> bool:
    """Prompt the user for FST download consent.

    Displays information about the FST and asks for confirmation.
    Returns True if the user consents, False otherwise.

    In non-interactive environments (no TTY), always returns False.
    """
    if not sys.stdin.isatty():
        return False

    entry = GIELLALT_FST_REGISTRY.get(lang_code, {})
    repo = entry.get("repo", f"giellalt/lang-{lang_code}")
    fmt = entry.get("format", "unknown")

    print()
    print("  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  FST Required — {lang_name} ({lang_code})")
    print("  │                                                             │")
    print("  │  This language has a GiellaLT morphological analyzer.       │")
    print("  │  FST validation is required for eval accuracy on            │")
    print("  │  polysynthetic and low-resource language targets.           │")
    print("  │                                                             │")
    print(f"  │  Source: https://github.com/{repo}")
    print(f"  │  Cache:  ~/.mt-eval/fsts/{lang_code}/")
    print("  │                                                             │")

    if fmt == "divvun":
        print("  │  ⚠ This language uses Divvun packaging.                    │")
        print("  │  Install the Divvun manager from https://divvun.no/        │")
        print("  │  Then extract .hfstol files to the cache directory above.  │")
        print("  └─────────────────────────────────────────────────────────────┘")
        return False

    print("  └─────────────────────────────────────────────────────────────┘")
    print()

    try:
        answer = input("  Download and install now? [y/N]: ").strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def ensure_fst_available(
    lang_code: str,
    lang_name: str,
    skip_fst: bool = False,
) -> Path | None:
    """Ensure the FST is available for the given language.

    This is the main entry point for the FST quality gate.

    Behavior:
        1. If FST is installed → return its path
        2. If FST is not installed and language has a known FST:
           a. If skip_fst=True → warn and return None
           b. Prompt user for download consent
           c. If yes → download, install, return path
           d. If no → return None (caller should abort eval)
        3. If no FST known for this language → return None (no gate)

    Args:
        lang_code: ISO 639-3 language code
        lang_name: Human-readable language name (for display)
        skip_fst: If True, skip the FST gate with a warning

    Returns:
        Path to FST cache directory, or None if not available
    """
    # Check if already installed
    if is_fst_installed(lang_code):
        fst_dir = get_fst_cache_dir(lang_code)
        analyzer = find_analyzer_hfstol(fst_dir)
        print(f"  FST: found ({analyzer.name}) at {fst_dir}")
        return fst_dir

    # Check if this language has a known FST
    if lang_code not in GIELLALT_FST_REGISTRY:
        # No FST registered — this isn't gated
        return None

    entry = GIELLALT_FST_REGISTRY[lang_code]

    # FST exists but not installed
    if skip_fst:
        print(f"  ⚠ FST: skipped (--skip-fst). {entry['name']} FST not installed.")
        print(f"    Results will lack morphological validation.")
        return None

    # Prompt for download
    if prompt_fst_install(lang_code, lang_name):
        try:
            fst_dir = install_fst(lang_code)
            print(f"  ✓ FST installed successfully at {fst_dir}")
            return fst_dir
        except Exception as e:
            print(f"  ✗ FST installation failed: {e}")
            return None
    else:
        # User declined or non-interactive — return None to signal gate failure
        return None
