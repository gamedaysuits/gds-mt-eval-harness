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

from corpora_builder import USER_AGENT
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
        resp = requests.head(url, timeout=10, allow_redirects=True,
                             headers={"User-Agent": USER_AGENT})
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

# Map from champollion language card codes to Tatoeba/OPUS corpus codes.
#
# POST-MIGRATION (ISO 639-3):
#   Card filenames are now 3-letter ISO 639-3 codes (e.g., "fra.json"),
#   which are also the Tatoeba/OPUS corpus codes. So most cards pass through
#   without needing an entry here.
#
#   Only entries where the CARD CODE differs from the Tatoeba code need
#   to appear:
#     - Regional variants (fra-CA → fra, spa-MX → spa)
#     - Macrolanguage cards that map to a different OPUS code
#     - Special cases (Bosnian/Serbian → Serbo-Croatian macro)
_CARD_TO_TATOEBA: dict[str, str] = {
    # Regional variants → Tatoeba's generic language code
    "fra-CA": "fra",      # Canadian French → Tatoeba's French
    "spa-MX": "spa",      # Mexican Spanish → Tatoeba's Spanish
    "por-PT": "por",      # European Portuguese → Tatoeba's Portuguese
    "por-BR": "por",      # Brazilian Portuguese → Tatoeba's Portuguese
    "cmn-Hant": "cmn",    # Traditional Chinese → Tatoeba's Mandarin

    # Macrolanguage → OPUS corpus code
    # (OPUS sometimes uses the macrolanguage code for corpus files)
    "nob": "nor",         # Norwegian Bokmål → OPUS uses 'nor'
    "nno": "nor",         # Norwegian Nynorsk → OPUS uses 'nor'
    "zsm": "msa",         # Standard Malay → OPUS uses 'msa'

    # Serbo-Croatian complex
    # OPUS stores all three under the macrolanguage code 'hbs'
    "bos": "hbs",         # Bosnian → OPUS Serbo-Croatian
    "srp": "hbs",         # Serbian → OPUS Serbo-Croatian
    "hrv": "hbs",         # Croatian → OPUS Serbo-Croatian
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
# Index-based probing (Tatoeba Challenge released-bitexts index)
# ---------------------------------------------------------------------------
#
# The Tatoeba Challenge release publishes a single index file listing
# every released bitext with its test/dev/train sentence-pair counts.
# One fetch answers "which pairs have enough data for a dev set?" for
# ALL pairs at once — exact counts, no per-pair HEAD requests. The HEAD
# probe above remains as a fallback for sources without an index.

#: Corpus-size floors from the corpus design spec §6.3 and the fair
#: scoring policy §5 (docs/TATOEBA_FAIR_SCORING_POLICY.md): below 100
#: evaluated entries, paired bootstrap significance tests cannot reliably
#: detect differences smaller than ~5 chrF++ points. 200+ is preferred
#: for detecting ~2-point differences at p<0.05.
FLOOR_N = 100
PREFERRED_N = 200

#: Fallback estimate of the fraction of raw test-split pairs that
#: survive the build pipeline (word-count filter, dedup, enrichment).
#: ``calibrate_survival()`` replaces this with the observed median from
#: already-built registry corpora when possible.
DEFAULT_SURVIVAL = 0.35


@dataclass
class IndexProbe:
    """Per-pair availability as recorded in the release index."""
    pair: str                 # alphabetical "lang1-lang2" key
    lang_a: str
    lang_b: str
    test_size: int
    dev_size: int
    train_size: int
    est_usable: int           # test_size x survival estimate
    tier: str                 # "preferred" | "floor" | "below-floor"


def fetch_release_index(
    cache_dir: str | Path,
    *,
    url: str | None = None,
    refresh: bool = False,
) -> Path:
    """Download (once) the released-bitexts index into the cache."""
    from corpora_builder.adapters.tatoeba_challenge_adapter import INDEX_URL

    url = url or INDEX_URL
    cache_dir = Path(cache_dir)
    path = cache_dir / url.rsplit("/", 1)[-1]
    if path.exists() and not refresh:
        return path
    cache_dir.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=60, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    path.write_bytes(resp.content)
    return path


def parse_release_index(path: str | Path) -> dict[str, dict]:
    """Parse released-bitexts.txt → {pair_key: {test/dev/train sizes}}.

    Columns: langpair, source-name, target-name, then (size, source
    token count, target token count) triples for test, dev, and train.
    Empty cells mean the release has no such split for the pair.

    Pair keys are normalised into ISO 639-3 space (the registry's code
    space): the release spells Mandarin ``zho``, so its pairs would
    otherwise never match a ``cmn`` lookup. See
    ``tatoeba_challenge_adapter.RELEASE_CODE_MAP``.
    """
    from corpora_builder.adapters.tatoeba_challenge_adapter import (
        iso_pair_key,
    )

    index: dict[str, dict] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 4 or "-" not in cols[0]:
            continue

        def _int(i: int) -> int:
            return int(cols[i]) if i < len(cols) and cols[i].strip() else 0

        index[iso_pair_key(cols[0])] = {
            "source_name": cols[1],
            "target_name": cols[2],
            "test_size": _int(3),
            "dev_size": _int(6),
            "train_size": _int(9),
        }
    return index


def _tier(est_usable: int) -> str:
    if est_usable >= PREFERRED_N:
        return "preferred"
    if est_usable >= FLOOR_N:
        return "floor"
    return "below-floor"


def probe_pairs_via_index(
    language_codes: list[str],
    index: dict[str, dict],
    *,
    survival: float = DEFAULT_SURVIVAL,
    available_pairs: set[str] | None = None,
) -> list[IndexProbe]:
    """Probe all unordered pairs among ``language_codes`` via the index.

    Args:
        language_codes: ISO 639-3 codes (Tatoeba-compatible).
        index: Parsed release index (``parse_release_index``).
        survival: Estimated build-pipeline survival fraction applied to
            the raw test-split count.
        available_pairs: Optional gate — restrict results to pairs whose
            test split is actually present in the consolidated test tar
            (``tatoeba_challenge_adapter.list_tar_pairs``); index rows
            and tar contents differ slightly at the small-pair tail.

    Returns:
        IndexProbe rows for every pair present in the index with a
        non-empty test split, sorted by est_usable descending.
    """
    codes = sorted(set(language_codes))
    results: list[IndexProbe] = []
    for i, lang_a in enumerate(codes):
        for lang_b in codes[i + 1:]:
            key = f"{min(lang_a, lang_b)}-{max(lang_a, lang_b)}"
            row = index.get(key)
            if not row or row["test_size"] <= 0:
                continue
            if available_pairs is not None and key not in available_pairs:
                continue
            est = int(row["test_size"] * survival)
            results.append(IndexProbe(
                pair=key,
                lang_a=min(lang_a, lang_b),
                lang_b=max(lang_a, lang_b),
                test_size=row["test_size"],
                dev_size=row["dev_size"],
                train_size=row["train_size"],
                est_usable=est,
                tier=_tier(est),
            ))
    results.sort(key=lambda r: (-r.est_usable, r.pair))
    return results


def calibrate_survival(
    registry_datasets: list[dict],
    index: dict[str, dict],
) -> float | None:
    """Median build-survival rate observed across existing corpora.

    Uses uncapped (size < 200) local Tatoeba corpora whose registry size
    does not exceed the raw test-split count — i.e. builds consistent
    with a test-split origin. Train-fallback builds (registry size above
    the test count, e.g. dan-fao) would corrupt the estimate and are
    excluded. Returns None when no usable samples exist.
    """
    samples: list[float] = []
    for ds in registry_datasets:
        lp = ds.get("language_pair")
        if not lp or ds.get("access") != "local":
            continue
        if "tatoeba" not in (ds.get("source") or "").lower():
            continue
        size = ds.get("size") or 0
        if not (0 < size < 200):
            continue
        key = "-".join(sorted((lp["source"], lp["target"])))
        test_size = index.get(key, {}).get("test_size", 0)
        if test_size >= size > 0:
            samples.append(size / test_size)
    if not samples:
        return None
    samples.sort()
    return samples[len(samples) // 2]


# ---------------------------------------------------------------------------
# Mesh analysis — which new pairs most improve translation chaining?
# ---------------------------------------------------------------------------
#
# The mission is "every language into every language by measured
# individual pair chains": a translation for an unbenchmarked pair
# (X, Y) is composed by chaining benchmarked edges X→…→Y, so the value
# of a NEW benchmarked pair is how much it shortens chains across the
# whole graph — not how big its corpus is.
#
# We measure that as the gain in *global efficiency*: the mean over all
# ordered node pairs of 1/d(u,v), with 1/∞ = 0 for disconnected pairs.
# Efficiency (unlike raw average path length) is well-defined on
# disconnected graphs, so edges that join components — the highest-value
# chaining edges of all — rank first instead of breaking the math.
# The same definition is used by the public sweep-queue generator
# (arena/scripts/generate_sweep_queue.py); a parity test in
# arena/tests keeps the two implementations in lockstep.

def graph_efficiency(nodes: list[str], edges: set[frozenset]) -> float:
    """Global efficiency of an undirected graph via per-node BFS."""
    from collections import deque

    adj: dict[str, set[str]] = {n: set() for n in nodes}
    for e in edges:
        pair = tuple(e)
        if len(pair) != 2:
            continue
        a, b = pair
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)

    n = len(nodes)
    if n < 2:
        return 0.0
    total = 0.0
    for start in nodes:
        dist = {start: 0}
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        total += sum(1.0 / d for node, d in dist.items() if node != start)
    return total / (n * (n - 1))


def chaining_gain(
    nodes: list[str],
    edges: set[frozenset],
    candidate: tuple[str, str],
    baseline: float | None = None,
) -> float:
    """Efficiency gain from adding one candidate edge to the graph."""
    if baseline is None:
        baseline = graph_efficiency(nodes, edges)
    a, b = candidate
    return graph_efficiency(nodes, edges | {frozenset((a, b))}) - baseline


def language_presence(index: dict[str, dict]) -> dict[str, int]:
    """Aggregate Tatoeba presence (test+train pairs) per language.

    Used to orient new corpora: the convention across the existing
    registry is that the higher-resource language is the source
    (eng→X, deu→ltz, spa→que, …) so evaluation measures translation
    INTO the lower-resource language. Presence is derived from the
    release index itself — no hardcoded language rankings.
    """
    presence: dict[str, int] = {}
    for key, row in index.items():
        a, b = key.split("-", 1)
        weight = row["test_size"] + row["train_size"]
        presence[a] = presence.get(a, 0) + weight
        presence[b] = presence.get(b, 0) + weight
    return presence


def _load_families(cards_dir: str | Path, langs: set[str]) -> dict[str, str]:
    """classification.family per language from champollion language cards."""
    fams: dict[str, str] = {}
    cards_path = Path(cards_dir)
    for lang in langs:
        card_file = cards_path / f"{lang}.json"
        if not card_file.exists():
            fams[lang] = "unknown"
            continue
        try:
            card = json.loads(card_file.read_text(encoding="utf-8"))
            fams[lang] = (card.get("classification") or {}).get(
                "family"
            ) or "unknown"
        except (OSError, json.JSONDecodeError):
            fams[lang] = "unknown"
    return fams


def mesh_report(
    registry_path: str | Path,
    cards_dir: str | Path,
    index: dict[str, dict],
    *,
    available_pairs: set[str] | None = None,
    survival: float | None = None,
) -> dict:
    """Rank candidate mesh edges between already-benchmarked languages.

    "Lit" nodes are the languages already covered by a registry corpus.
    Candidates are unordered lit-lit pairs with no existing corpus in
    either direction and a non-empty test split in the release (and in
    the consolidated tar when ``available_pairs`` is given). Each is
    scored by chaining gain (global-efficiency delta), flagged when it
    bridges two language families, and given a recommended direction
    (higher Tatoeba presence → source).

    Also reports "hub candidates": not-yet-benchmarked languages ranked
    by how many lit languages they share an adequate test split with
    and how many families those connections span — the languages whose
    addition would open the most new chains.
    """
    registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    datasets = registry.get("datasets", [])

    lit: set[str] = set()
    existing_edges: set[frozenset] = set()
    for ds in datasets:
        lp = ds.get("language_pair")
        if not lp:
            continue
        lit |= {lp["source"], lp["target"]}
        existing_edges.add(frozenset((lp["source"], lp["target"])))

    nodes = sorted(lit)
    baseline = graph_efficiency(nodes, existing_edges)
    surv = survival
    if surv is None:
        surv = calibrate_survival(datasets, index) or DEFAULT_SURVIVAL

    presence = language_presence(index)
    families = _load_families(cards_dir, lit)

    candidates = []
    for probe in probe_pairs_via_index(
        nodes, index, survival=surv, available_pairs=available_pairs,
    ):
        if frozenset((probe.lang_a, probe.lang_b)) in existing_edges:
            continue
        gain = chaining_gain(
            nodes, existing_edges, (probe.lang_a, probe.lang_b), baseline,
        )
        fam_a = families.get(probe.lang_a, "unknown")
        fam_b = families.get(probe.lang_b, "unknown")
        src, tgt = (
            (probe.lang_a, probe.lang_b)
            if presence.get(probe.lang_a, 0) >= presence.get(probe.lang_b, 0)
            else (probe.lang_b, probe.lang_a)
        )
        candidates.append({
            "pair": probe.pair,
            "direction": f"{src}>{tgt}",
            "source": src,
            "target": tgt,
            "test_size": probe.test_size,
            "dev_size": probe.dev_size,
            "train_size": probe.train_size,
            "est_usable": probe.est_usable,
            "tier": probe.tier,
            "chaining_gain": round(gain, 6),
            "bridges_families": (
                fam_a != fam_b
                if "unknown" not in (fam_a, fam_b) else None
            ),
            "families": sorted({fam_a, fam_b}),
        })
    candidates.sort(key=lambda c: (-c["chaining_gain"], -c["est_usable"], c["pair"]))

    # Hub candidates: unlit languages that would connect many lit nodes.
    hub_scores: dict[str, dict] = {}
    lit_set = set(nodes)
    for key, row in index.items():
        if row["test_size"] * surv < FLOOR_N:
            continue
        if available_pairs is not None and key not in available_pairs:
            continue
        a, b = key.split("-", 1)
        for newcomer, lit_side in ((a, b), (b, a)):
            if newcomer in lit_set or lit_side not in lit_set:
                continue
            entry = hub_scores.setdefault(
                newcomer, {"language": newcomer, "lit_connections": 0,
                           "connects_to": []},
            )
            entry["lit_connections"] += 1
            entry["connects_to"].append(lit_side)
    hubs = sorted(
        hub_scores.values(),
        key=lambda h: (-h["lit_connections"], h["language"]),
    )[:25]
    lit_families = _load_families(cards_dir, lit_set)
    for hub in hubs:
        hub["families_reached"] = sorted({
            lit_families.get(l, "unknown") for l in hub["connects_to"]
        })

    return {
        "generated_by": "corpora_builder.probe_tatoeba mesh_report",
        "registry": str(registry_path),
        "lit_languages": nodes,
        "existing_edge_count": len(existing_edges),
        "baseline_global_efficiency": round(baseline, 6),
        "survival_rate": round(surv, 4),
        "survival_basis": (
            "median built/raw ratio of existing uncapped test-split corpora"
            if survival is None else "explicit --survival override"
        ),
        "floors": {"floor": FLOOR_N, "preferred": PREFERRED_N},
        "candidates": candidates,
        "hub_candidates": hubs,
    }


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
    parser.add_argument(
        "--index",
        action="store_true",
        help="Probe via the Tatoeba Challenge released-bitexts index "
             "(one fetch, exact per-pair counts) instead of HTTP HEADs.",
    )
    parser.add_argument(
        "--mesh",
        metavar="REGISTRY_JSON",
        help="Mesh mode: rank candidate edges between languages already "
             "benchmarked in the given registry (implies --index). "
             "Requires --language-cards-dir for family lookups.",
    )
    parser.add_argument(
        "--cache-dir",
        default="arena/datasets/.cache/tatoeba-challenge",
        help="Cache directory for the index/tar downloads.",
    )
    parser.add_argument(
        "--survival",
        type=float,
        default=None,
        help="Override the build-survival estimate (default: calibrate "
             "from the registry, falling back to %.2f)." % DEFAULT_SURVIVAL,
    )

    args = parser.parse_args()

    # ---- Index / mesh modes ----------------------------------------------
    if args.mesh or args.index:
        index_path = fetch_release_index(args.cache_dir)
        index = parse_release_index(index_path)

        available: set[str] | None = None
        try:
            from corpora_builder.adapters.tatoeba_challenge_adapter import (
                iso_pair_key,
                list_tar_pairs,
            )
            tar = Path(args.cache_dir) / "test-v2023-09-26.tar"
            if tar.exists():
                available = {iso_pair_key(p) for p in list_tar_pairs(tar)}
        except Exception:  # pragma: no cover — availability gate is optional
            available = None

        if args.mesh:
            if not args.language_cards_dir:
                print("Error: --mesh requires --language-cards-dir.",
                      file=sys.stderr)
                sys.exit(1)
            report = mesh_report(
                args.mesh,
                args.language_cards_dir,
                index,
                available_pairs=available,
                survival=args.survival,
            )
            print(f"  Lit languages: {len(report['lit_languages'])}; "
                  f"existing edges: {report['existing_edge_count']}; "
                  f"baseline efficiency: {report['baseline_global_efficiency']}")
            print(f"  Survival rate: {report['survival_rate']} "
                  f"({report['survival_basis']})")
            print(f"  Candidates: {len(report['candidates'])} "
                  f"(top 15 by chaining gain):")
            for c in report["candidates"][:15]:
                print(f"    {c['direction']:<12} gain={c['chaining_gain']:.6f} "
                      f"test={c['test_size']:>6} tier={c['tier']}")
            if args.output:
                out = Path(args.output)
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(
                    json.dumps(report, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                print(f"\n  Mesh report written to: {out}")
            return

        # Plain --index probe
        if args.langs:
            codes = args.langs
        elif args.language_cards_dir:
            codes = load_language_codes_from_cards(args.language_cards_dir)
        else:
            print("Error: Provide --language-cards-dir or --langs.",
                  file=sys.stderr)
            sys.exit(1)
        survival = args.survival if args.survival is not None else DEFAULT_SURVIVAL
        probes = probe_pairs_via_index(
            codes, index, survival=survival, available_pairs=available,
        )
        print(f"  {len(probes)} pairs with test data among {len(codes)} languages")
        for p in probes[:30]:
            print(f"    {p.pair:<12} test={p.test_size:>6} "
                  f"est~{p.est_usable:>5} {p.tier}")
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({
                "probe_mode": "index",
                "survival_rate": survival,
                "floors": {"floor": FLOOR_N, "preferred": PREFERRED_N},
                "pairs": [asdict(p) for p in probes],
            }, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\n  Report written to: {out}")
        return

    # ---- Legacy HEAD-probe mode ------------------------------------------
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
