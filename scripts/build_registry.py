#!/usr/bin/env python3
"""
Build split registry files from corpora cards.

Reads all corpora cards from cli/shared/corpora-cards/ and generates
per-source registry files in arena/datasets/:

    registry-prize.json     — EdTeKLA + community-curated prize corpora
    registry-tatoeba.json   — Tatoeba Challenge pairs (eval cards)
    registry-flores.json    — FLORES+ multiway expansion (multiway card)
    registry-ntrex.json     — NTREX-128 multiway expansion (multiway card)

Each registry file has the same shape:
    { "registry_version": "3.0.0", "datasets": [...] }

The harness's load_registry() merges them at runtime.

Why split?
    1. Contaminated sources (FLORES, NTREX) are easily excludable from
       mesh efficiency calculations — just don't load those files
    2. Prize corpora (EdTeKLA) are separate from dev-baseline corpora
    3. Each file is independently diffable and auditable

SSOT: one truth, one place — edit the card, rebuild the registries.

Usage:
    python arena/scripts/build_registry.py           # build all
    python arena/scripts/build_registry.py --dry-run  # preview without writing
    python arena/scripts/build_registry.py --diff     # show diff against current
"""

import json
import sys
from pathlib import Path

# --- Paths ---
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
CARDS_DIR = REPO_ROOT / "cli" / "shared" / "corpora-cards"
REGISTRY_DIR = REPO_ROOT / "arena" / "datasets"
CODE_BRIDGE_PATH = REPO_ROOT / "cli" / "shared" / "code-bridge.json"

# Legacy single-file path (for --diff comparison)
LEGACY_REGISTRY_PATH = REGISTRY_DIR / "registry.json"

# Bundled copy shipped INSIDE the package, so `pip install mt-eval-harness`
# carries a registry with no monorepo present (config.load_registry resolution
# step 3 — the offline fallback under the remote fetch). Gitignored; generated.
BUNDLED_REGISTRY_PATH = REPO_ROOT / "arena" / "mt_eval_harness" / "data" / "registry.json"

# --- Flags ---
DRY_RUN = "--dry-run" in sys.argv
SHOW_DIFF = "--diff" in sys.argv


# ---------------------------------------------------------------------------
# Code bridge — maps external source codes to project ISO 639-3
# ---------------------------------------------------------------------------

def load_code_bridge() -> dict:
    """Load the SSOT code mapping from cli/shared/code-bridge.json.

    Returns a dict keyed by source namespace ("flores", "ntrex", "tatoeba"),
    each mapping external codes to ISO 639-3 project codes.
    Falls back to empty mappings if the file doesn't exist yet.
    """
    if not CODE_BRIDGE_PATH.exists():
        return {}
    return json.loads(CODE_BRIDGE_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Registry source classification
# ---------------------------------------------------------------------------

# Determines which split registry file a card's entries go into.
# The classification is based on the card id and type.
_SOURCE_CLASSIFIERS = {
    # EdTeKLA and community prize corpora → prize
    "edtekla": "prize",
    "prize": "prize",
    # GlobalVoices citizen journalism (CC-BY-4.0, news domain)
    "globalvoices": "globalvoices",
    # Gamayun / CLEAR Global humanitarian kits (CC-BY-4.0)
    "gamayun": "gamayun",
}


def classify_registry_source(card: dict) -> str:
    """Determine which split registry file a card belongs to.

    Returns one of: 'prize', 'tatoeba', 'flores', 'ntrex', or 'tatoeba'
    (default for unclassified eval cards).
    """
    card_id = card.get("id", "")
    card_type = card.get("type", "")

    # Multiway cards are named by their source
    if card_type == "multiway":
        if "flores" in card_id:
            return "flores"
        if "ntrex" in card_id:
            return "ntrex"
        # Generic multiway — use card id prefix
        return card_id.split("-")[1] if "-" in card_id else "other"

    # Eval cards — classify by known prefixes
    for prefix, source in _SOURCE_CLASSIFIERS.items():
        if prefix in card_id:
            return source

    # Default: Tatoeba-derived dev corpora
    return "tatoeba"


# ---------------------------------------------------------------------------
# Card → registry entry conversion (eval cards)
# ---------------------------------------------------------------------------

def card_to_registry_entry(card: dict) -> dict:
    """Convert an eval-type corpora card to a registry entry.

    The registry entry preserves backward compatibility with the
    existing resolve_dataset() function in config.py, while carrying
    through fetch-from-source build metadata, richness metrics, and
    aliases that cards store.
    """
    pair = card.get("pair", {})
    dev = card.get("dev", {})
    source = card.get("source", {})

    # Convert proportional domain distribution back to the registry's
    # count format if we have both proportions and size
    domain_dist = {}
    raw_dist = dev.get("domainDistribution", {})
    size = dev.get("size", 0)
    if raw_dist and size:
        for domain, proportion in raw_dist.items():
            domain_dist[domain] = round(proportion * size)

    # Extract sovereignty and usage restriction fields
    sovereignty = card.get("sovereignty") or {}
    usage = card.get("usageRestrictions") or {}

    # Determine access mode and sha256 from the card's source block
    has_build_recipe = bool(source.get("repo_url") and source.get("builder"))
    access = "fetch-from-source" if has_build_recipe else "local"
    sha256 = source.get("sha256")

    # Build the source_export block for fetch-from-source corpora
    source_export = None
    if has_build_recipe:
        source_export = {
            "builder": source.get("builder"),
            "url": source.get("repo_url"),
            "sha256": source.get("archive_sha256") or (
                # For Tatoeba Challenge corpora, the archive sha256 is the
                # well-known consolidated test archive pin
                "9eef2fb5fe4551401de3675d8e98ad0e9455d063ab51c77ad85870f4b38a39f2"
                if source.get("builder") == "tatoeba-challenge" else None
            ),
            "member": source.get("member"),
            "license": source.get("license"),
            "license_url": source.get("license_url"),
        }
        recipe = source.get("recipe")
        if recipe:
            source_export["recipe"] = recipe

    # Build the registry entry
    entry = {
        "id": card["id"],
        "name": card["name"],
        "version": card["version"],
        "language_pair": {
            "source": pair.get("source", "unk"),
            "target": pair.get("target", "unk")
        },
        "size": dev.get("size", 0),
        "domain": dev.get("domain", "mixed"),
        "domain_distribution": domain_dist if domain_dist else None,
        "url": None,
        "sha256": sha256,
        "access": access,
        "do_not_train": card.get("doNotTrain", True),
        "license": card.get("license", {}).get("spdx", ""),
        "source": source.get("publisher", ""),
        "path": dev.get("dataFile", ""),
        "segment": "development",
        "notes": card.get("description", ""),
        "attribution": f"{source.get('publisher', '')} ({card.get('license', {}).get('spdx', '')})",
        # OCAP-forward sovereignty fields
        "sovereignty_frameworks": sovereignty.get("frameworks", []),
        "usage_training": usage.get("training"),
        "usage_commercial": usage.get("commercialUse"),
        "community_notes": usage.get("communityNotes"),
    }

    # Contamination level — carried through so downstream consumers
    # (queue ranking, leaderboard badges) can reason about it without
    # re-reading cards. Cards use either 'level' or 'risk' for the grade.
    contam = card.get("contamination") or {}
    contam_level = contam.get("level") or contam.get("risk")
    if contam_level:
        entry["contamination"] = contam_level

    # Quarantine flag — an explicit, acknowledged "catalogued but not
    # runnable" marker. The queue (queue_corpora) skips quarantined sets;
    # the buildability gate exempts them from the builder-exists check but
    # reports them loudly. Carrying the reason keeps the audit trail.
    if card.get("quarantine"):
        entry["quarantine"] = True
        if card.get("quarantineReason"):
            entry["quarantine_reason"] = card["quarantineReason"]

    # Aliases for dataset resolution (e.g., "edtekla-dev" → "eval-eng-crk-edtekla-dev-v1")
    aliases = card.get("aliases")
    if aliases:
        entry["aliases"] = aliases

    # Source export for fetch-from-source corpora
    if source_export:
        entry["source_export"] = source_export

    # Richness metrics for queue prioritization
    richness = card.get("richness")
    if richness:
        entry["richness"] = richness

    return entry


# ---------------------------------------------------------------------------
# Multiway card → registry entries expansion
# ---------------------------------------------------------------------------

def expand_multiway_card(card: dict, code_bridge: dict) -> list[dict]:
    """Expand a multiway card into per-pair registry entries.

    One multiway card with N languages produces N×(N-1) registry entries —
    one per ordered (source, target) pair where source ≠ target.

    The code bridge maps external source codes (e.g., FLORES 'zho_Hans')
    to project ISO 639-3 codes (e.g., 'cmn-Hans'). Codes not in the
    bridge pass through unchanged — they're assumed to already be ISO 639-3.
    """
    languages = card.get("languages", [])
    gen = card.get("pairGeneration", {})
    source = card.get("source", {})
    download = card.get("download", {})

    # Determine which code bridge namespace to use
    bridge_namespace = ""
    card_id = card.get("id", "")
    if "flores" in card_id:
        bridge_namespace = "flores"
    elif "ntrex" in card_id:
        bridge_namespace = "ntrex"

    bridge_map = code_bridge.get(bridge_namespace, {})

    # Builder id namespace. flores/ntrex carry code bridges and registered
    # parallel-text builders; other multiway sources (in22, tico19, …) derive
    # their builder id from the card's source token so the dispatch — and any
    # "builder not implemented" warning — names the actual source rather than
    # an empty "-parallel". An unimplemented builder fails loudly at fetch
    # time (corpus_fetch raises on unknown builder ids); these sets are
    # contaminated catalogue corpora kept out of the queue regardless.
    if bridge_namespace:
        builder_ns = bridge_namespace
    else:
        parts = card_id.split("-")
        builder_ns = parts[1] if len(parts) > 1 else "multiway"

    # Deduplicate pairs where different source codes map to the same ISO code
    # (e.g., zho_Hans and zho_Hant both → cmn)
    seen_pairs = set()
    entries = []

    for src_code in languages:
        iso_src = bridge_map.get(src_code, src_code)
        for tgt_code in languages:
            if src_code == tgt_code:
                continue
            iso_tgt = bridge_map.get(tgt_code, tgt_code)

            # Skip self-pairs after mapping (e.g., zho_Hans→cmn, zho_Hant→cmn)
            if iso_src == iso_tgt:
                continue

            pair_key = (iso_src, iso_tgt)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            entries.append({
                "id": f"{card['id']}-{iso_src}-{iso_tgt}",
                "name": f"{card['name']} {iso_src}→{iso_tgt}",
                "version": card["version"],
                "language_pair": {"source": iso_src, "target": iso_tgt},
                "size": gen.get("sizePerPair", 0),
                "domain": gen.get("domain", "mixed"),
                "domain_distribution": None,
                "url": None,
                "sha256": None,
                "access": "fetch-from-source",
                "do_not_train": gen.get("doNotTrain", True),
                "license": card.get("license", {}).get("spdx", ""),
                "source": source.get("publisher", ""),
                "path": f"{card['id']}/{iso_src}-{iso_tgt}.json",
                "segment": gen.get("segment", "devtest"),
                "notes": card.get("description", ""),
                "attribution": f"{source.get('publisher', '')} ({card.get('license', {}).get('spdx', '')})",
                # Back-reference to the multiway card for fetch-time resolution
                "multiway_card": card["id"],
                # Preserve original source codes for fetch-time file resolution
                "source_codes": {"source": src_code, "target": tgt_code},
                # Builder dispatch for corpus_fetch
                "source_export": {
                    "builder": f"{builder_ns}-parallel",
                    "url": download.get("url"),
                    "file_pattern": download.get("filePattern"),
                    "format": download.get("format", "parallel-text"),
                    "segment": gen.get("segment", "devtest"),
                },
            })

    return entries


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_card(card: dict, card_name: str) -> list[str]:
    """Validate sovereignty consistency rules on a card.

    Returns a list of error messages. Empty list = card is valid.
    These rules enforce consistency between sovereignty-related fields
    that the JSON schema alone can't express (cross-field constraints).
    """
    errors = []
    card_id = card.get("id", card_name)

    # Rule 1: doNotTrain and usageRestrictions.training must be consistent.
    do_not_train = card.get("doNotTrain")
    usage = card.get("usageRestrictions") or {}
    training = usage.get("training")
    if do_not_train and training == "permitted":
        errors.append(
            f"{card_id}: doNotTrain=true but usageRestrictions.training='permitted' "
            f"— these are contradictory. If eval data shouldn't be trained on, "
            f"training can't be 'permitted'."
        )

    # Rule 2: Cards invoking OCAP framework should not have training='permitted'.
    sovereignty = card.get("sovereignty") or {}
    frameworks = sovereignty.get("frameworks", [])
    if "OCAP" in frameworks and training == "permitted":
        errors.append(
            f"{card_id}: sovereignty.frameworks includes 'OCAP' but "
            f"usageRestrictions.training='permitted' — OCAP-governed data "
            f"should have community-asserted training restrictions."
        )

    # Rule 3: Active secretTest requires stewardship with ≥5 stewards.
    secret_test = card.get("secretTest")
    if secret_test and secret_test.get("status") == "active":
        stewardship = card.get("stewardship") or {}
        stewards = stewardship.get("stewards", [])
        if len(stewards) < 5:
            errors.append(
                f"{card_id}: secretTest.status='active' but only "
                f"{len(stewards)} stewards (need ≥5). Prize corpora with "
                f"active secret sets require 5+ stewards for TSS custody."
            )
        if not stewardship.get("threshold"):
            errors.append(
                f"{card_id}: secretTest.status='active' but stewardship.threshold "
                f"is not set. Must specify TSS threshold (e.g., '3 of 5')."
            )

    return errors


# ---------------------------------------------------------------------------
# Buildability gate — the registry may not advertise corpora it can't serve
# ---------------------------------------------------------------------------
#
# The promise this gate enforces: *every corpus that can reach the public
# queue must be buildable or already present on disk.* A silent
# access:"local" entry pointing at a file that isn't there, or a
# fetch-from-source entry naming a builder the harness doesn't implement,
# is exactly the "looks registered but can't run" failure we refuse to ship.
# Errors block the build (exit 1). Catalogue-only corpora (contaminated
# multiway test sets, quarantined sets) are never queue-eligible, so their
# build gaps are reported as warnings rather than hard failures.


def registered_builders() -> set:
    """Builder ids the harness can actually dispatch (the SSOT for fetch).

    Imported live from ``mt_eval_harness.corpus_fetch`` so the registry can
    never claim a builder that has no implementation. We refuse to build a
    registry we cannot validate — a missing import is fatal, not skipped.
    """
    arena_dir = REPO_ROOT / "arena"
    if str(arena_dir) not in sys.path:
        sys.path.insert(0, str(arena_dir))
    try:
        from mt_eval_harness import corpus_fetch
    except Exception as exc:
        raise SystemExit(
            f"FATAL: cannot import mt_eval_harness.corpus_fetch to validate "
            f"builder ids ({exc}). build_registry refuses to run without the "
            f"harness's builder registry — fix the import before building."
        )
    return set(corpus_fetch.BUILDERS) | set(corpus_fetch.REGISTRY_BUILDERS)


def _entry_is_queue_eligible(entry: dict) -> bool:
    """Mirror of generate_sweep_queue.queue_corpora's eligibility test.

    Kept deliberately in sync: the gate's whole promise is "if an entry can
    reach the queue, it must be buildable", so it must judge eligibility the
    same way the queue does.
    """
    if entry.get("quarantine"):
        return False
    access = entry.get("access")
    if access == "fetch-from-source":
        if not isinstance(entry.get("source_export"), dict):
            return False
    elif access != "local":
        return False
    if entry.get("segment") != "development":
        return False
    if "NC" in (entry.get("license") or "").upper():
        return False
    if not entry.get("path"):
        return False
    return True


def _local_file_exists(entry: dict) -> bool:
    """True when an access:local entry's content file is present on disk."""
    path = entry.get("path")
    if not path:
        return False
    candidates = [
        REGISTRY_DIR / path,
        REGISTRY_DIR / "curated" / Path(path).name,
        REPO_ROOT / path,
    ]
    return any(p.is_file() for p in candidates)


def gate_entries(source_entries: dict, known_builders: set):
    """Loud integrity gate over generated registry entries.

    Returns ``(errors, catalogue_gaps, quarantined)``:
        errors          — list[str]; queue-eligible entries that can't be
                          built/loaded. ANY of these blocks the build.
        catalogue_gaps  — dict[(source, reason, detail) -> count]; non-queue
                          catalogue corpora (e.g. contaminated multiway) with
                          no working builder. Reported, not fatal.
        quarantined     — dict[source -> count]; explicitly shelved corpora.
    """
    errors: list[str] = []
    catalogue: dict = {}
    quarantined: dict = {}

    for source, entries in source_entries.items():
        for e in entries:
            eid = e.get("id", "?")
            if e.get("quarantine"):
                quarantined[source] = quarantined.get(source, 0) + 1
                continue

            access = e.get("access")
            problem = None  # (reason, detail)
            if access == "fetch-from-source":
                builder = (e.get("source_export") or {}).get("builder")
                if not builder:
                    problem = ("missing source_export.builder", None)
                elif builder not in known_builders:
                    problem = ("unregistered builder", builder)
            elif access == "local":
                if not _local_file_exists(e):
                    problem = ("missing local content file", e.get("path"))
            else:
                problem = ("unexpected access mode", access)

            if problem is None:
                continue
            reason, detail = problem
            if _entry_is_queue_eligible(e):
                errors.append(
                    f"  ✗ {eid}: {reason}"
                    + (f" '{detail}'" if detail else "")
                    + "  — this corpus is QUEUE-ELIGIBLE and MUST be buildable."
                )
            else:
                key = (source, reason, detail)
                catalogue[key] = catalogue.get(key, 0) + 1

    return errors, catalogue, quarantined


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not CARDS_DIR.exists():
        print(f"ERROR: Cards directory not found: {CARDS_DIR}")
        sys.exit(1)

    code_bridge = load_code_bridge()

    # Load all cards (eval + multiway), skip reference cards
    eval_cards = []
    multiway_cards = []
    self_pair_cards = []  # source == target — invalid for translation eval

    for card_path in sorted(CARDS_DIR.glob("*.json")):
        try:
            card = json.loads(card_path.read_text(encoding="utf-8"))
            card_type = card.get("type")
            if card_type == "eval":
                pair = card.get("pair") or {}
                if pair.get("source") and pair.get("source") == pair.get("target"):
                    # A same-language "translation" pair is not a translation
                    # direction: it would be a self-loop in the mesh and a
                    # meaningless queue item. Exclude it from every registry
                    # rather than let it pollute the queue / crash the mesh.
                    self_pair_cards.append(card.get("id", card_path.name))
                    continue
                eval_cards.append(card)
            elif card_type == "multiway":
                multiway_cards.append(card)
            # reference cards are skipped — they don't produce registry entries
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  WARN Skipping {card_path.name}: {e}")

    print(f"Found {len(eval_cards)} eval cards, {len(multiway_cards)} multiway cards in {CARDS_DIR}")

    if self_pair_cards:
        print(
            f"\nEXCLUDED {len(self_pair_cards)} self-pair card(s) "
            f"(source == target — not a valid translation direction). These "
            f"are not emitted to any registry; delete the cards to silence "
            f"this notice:"
        )
        for cid in sorted(self_pair_cards):
            print(f"  ⚠ {cid}")

    # Validate sovereignty consistency rules on eval cards
    all_errors = []
    for card in eval_cards:
        card_errors = validate_card(card, card.get("id", "unknown"))
        all_errors.extend(card_errors)

    if all_errors:
        print(f"\nSOVEREIGNTY VALIDATION ERRORS ({len(all_errors)}):")
        for err in all_errors:
            print(f"  ✗ {err}")
        print("\nFix the cards above before rebuilding the registry.")
        sys.exit(1)
    else:
        print("Sovereignty validation: OK")

    # --- Build per-source registry entries ---
    # Group eval card entries by their registry source
    source_entries: dict[str, list[dict]] = {}

    for card in eval_cards:
        source = classify_registry_source(card)
        entry = card_to_registry_entry(card)
        source_entries.setdefault(source, []).append(entry)

    # Expand multiway cards and add their entries
    for card in multiway_cards:
        source = classify_registry_source(card)
        entries = expand_multiway_card(card, code_bridge)
        source_entries.setdefault(source, []).extend(entries)
        print(f"  Expanded multiway card '{card['id']}' → {len(entries)} entries → registry-{source}.json")

    # --- Buildability gate: refuse to advertise corpora we can't serve ---
    known_builders = registered_builders()
    errors, catalogue_gaps, quarantined = gate_entries(source_entries, known_builders)

    if quarantined:
        total_q = sum(quarantined.values())
        print(f"\nQuarantined (catalogued, explicitly NOT runnable) — {total_q} entries:")
        for src, n in sorted(quarantined.items()):
            print(f"  ⚠ registry-{src}.json: {n} quarantined")

    if catalogue_gaps:
        total_c = sum(catalogue_gaps.values())
        print(f"\nCatalogue-only build gaps (NOT queue-eligible, e.g. contaminated "
              f"multiway) — {total_c} entries:")
        for (src, reason, detail), n in sorted(catalogue_gaps.items()):
            d = f" '{detail}'" if detail else ""
            print(f"  ⚠ registry-{src}.json: {n}× {reason}{d}")

    if errors:
        print(f"\nBUILDABILITY GATE FAILED — {len(errors)} queue-eligible "
              f"corpora cannot be built or loaded:")
        for err in errors:
            print(err)
        print("\nA corpus that can reach the public queue MUST be runnable. "
              "Fix the card (recipe/builder) or mark it quarantine:true before "
              "rebuilding.")
        sys.exit(1)
    print("\nBuildability gate: OK — every queue-eligible corpus is buildable.")

    # --- Output ---
    total_entries = sum(len(entries) for entries in source_entries.values())

    if DRY_RUN:
        print(f"\nDry run — would write {total_entries} entries across {len(source_entries)} registry files:")
        for source, entries in sorted(source_entries.items()):
            print(f"  registry-{source}.json: {len(entries)} entries")
        return

    if SHOW_DIFF:
        # Compare against legacy single-file registry if it exists
        if LEGACY_REGISTRY_PATH.exists():
            import difflib
            old = LEGACY_REGISTRY_PATH.read_text(encoding="utf-8").splitlines()

            # Build a merged view for comparison
            merged = {"registry_version": "3.0.0", "datasets": []}
            for entries in source_entries.values():
                merged["datasets"].extend(entries)
            new = json.dumps(merged, indent=2, ensure_ascii=False).splitlines()

            diff = difflib.unified_diff(
                old, new,
                fromfile="registry.json (current)",
                tofile="registry-*.json (rebuilt, merged view)",
                lineterm="",
            )
            diff_lines = list(diff)
            if diff_lines:
                # Show first 100 lines to avoid overwhelming output
                for line in diff_lines[:100]:
                    print(line)
                if len(diff_lines) > 100:
                    print(f"... ({len(diff_lines) - 100} more diff lines)")
            else:
                print("No changes.")
        else:
            print("No legacy registry.json to diff against.")
        return

    # Write split registry files
    for source, entries in sorted(source_entries.items()):
        registry = {
            "registry_version": "3.0.0",
            "_generated": (
                f"Built from cli/shared/corpora-cards/ by build_registry.py. "
                f"DO NOT EDIT — edit the corpora cards instead. "
                f"Source: {source}."
            ),
            "datasets": entries,
        }
        output_path = REGISTRY_DIR / f"registry-{source}.json"
        output = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
        output_path.write_text(output, encoding="utf-8")
        print(f"  Wrote registry-{source}.json: {len(entries)} entries")

    # Write the merged single-file registry.json — the current dev/runnable
    # registry (every development-segment entry across all sources, tagged
    # with registry_source). This is what the legacy single-file consumers
    # read: load_registry()'s single-file mode, generate_sweep_queue,
    # lint_run_reports, and corpus_fetch's registry fallback. Regenerating it
    # from the cards is what stops those consumers from going stale.
    #
    # Contaminated multiway catalogue (FLORES/NTREX/IN22/TICO19, all
    # devtest/test segment) is deliberately EXCLUDED here so it never enters
    # the queue or the mesh-efficiency calculations — it stays addressable
    # only via its registry-*.json split file, on explicit demand.
    merged_datasets = []
    for source, entries in sorted(source_entries.items()):
        for e in entries:
            if e.get("segment") == "development":
                tagged = dict(e)
                tagged["registry_source"] = source
                merged_datasets.append(tagged)
    merged = {
        "registry_version": "3.0.0",
        "_generated": (
            "Built from cli/shared/corpora-cards/ by build_registry.py. "
            "DO NOT EDIT — edit the corpora cards instead. Merged "
            "development-segment (runnable) registry; contaminated multiway "
            "catalogue lives only in registry-*.json split files."
        ),
        "datasets": merged_datasets,
    }
    merged_json = json.dumps(merged, indent=2, ensure_ascii=False) + "\n"
    LEGACY_REGISTRY_PATH.write_text(merged_json, encoding="utf-8")
    print(f"  Wrote registry.json (merged dev/runnable): {len(merged_datasets)} entries")

    # Bundled copy inside the package — what a `pip install`ed harness ships
    # with when there's no monorepo (config.load_registry step 3). Same content.
    BUNDLED_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    BUNDLED_REGISTRY_PATH.write_text(merged_json, encoding="utf-8")
    print(f"  Wrote {BUNDLED_REGISTRY_PATH.relative_to(REPO_ROOT)} (bundled fallback)")

    print(f"\nTotal: {total_entries} entries across {len(source_entries)} split "
          f"files + {len(merged_datasets)} in the merged registry.json")


if __name__ == "__main__":
    main()
