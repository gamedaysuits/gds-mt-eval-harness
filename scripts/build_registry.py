#!/usr/bin/env python3
"""
Build arena/datasets/registry.json from corpora cards.

Reads all eval-type corpora cards from cli/shared/corpora-cards/ and
generates the flat registry.json that the harness resolver uses. This
makes registry.json a GENERATED artifact — the cards are the SSOT.

Why generate instead of editing registry.json directly:
    1. Cards are individual files — easier to review, diff, and attribute
    2. Cards have richer metadata (contamination, stewardship) that the
       registry doesn't need but humans do
    3. The registry format is optimized for the harness resolver, not for
       human comprehension
    4. SSOT: one truth, one place — edit the card, rebuild the registry

Usage:
    python arena/scripts/build_registry.py           # build
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
REGISTRY_PATH = REPO_ROOT / "arena" / "datasets" / "registry.json"

# --- Flags ---
DRY_RUN = "--dry-run" in sys.argv
SHOW_DIFF = "--diff" in sys.argv


def card_to_registry_entry(card: dict) -> dict:
    """Convert a corpora card to a registry.json entry.

    Only eval-type cards produce registry entries — reference cards
    are informational only and don't resolve to loadable datasets.

    The registry entry preserves backward compatibility with the
    existing resolve_dataset() function in config.py.
    """
    pair = card.get("pair", {})
    dev = card.get("dev", {})

    # Convert proportional domain distribution back to the registry's
    # count format if we have both proportions and size
    domain_dist = {}
    raw_dist = dev.get("domainDistribution", {})
    size = dev.get("size", 0)
    if raw_dist and size:
        for domain, proportion in raw_dist.items():
            domain_dist[domain] = round(proportion * size)

    # Extract sovereignty and usage restriction fields
    # These are the new OCAP-forward fields — they may not exist on
    # legacy cards, so we default to None/empty for backward compat.
    sovereignty = card.get("sovereignty") or {}
    usage = card.get("usageRestrictions") or {}

    return {
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
        "sha256": None,
        "access": "local",
        "do_not_train": card.get("doNotTrain", True),
        "license": card.get("license", {}).get("spdx", ""),
        "source": card.get("source", {}).get("publisher", ""),
        "path": dev.get("dataFile", ""),
        "segment": "development",
        "notes": card.get("description", ""),
        # OCAP-forward sovereignty fields (v2.1.0)
        "sovereignty_frameworks": sovereignty.get("frameworks", []),
        "usage_training": usage.get("training"),
        "usage_commercial": usage.get("commercialUse"),
        "community_notes": usage.get("communityNotes")
    }


def validate_card(card: dict, card_name: str) -> list[str]:
    """Validate sovereignty consistency rules on a card.

    Returns a list of error messages. Empty list = card is valid.
    These rules enforce consistency between sovereignty-related fields
    that the JSON schema alone can't express (cross-field constraints).
    """
    errors = []
    card_id = card.get("id", card_name)

    # Rule 1: doNotTrain and usageRestrictions.training must be consistent.
    # If doNotTrain is true, training must not be 'permitted'.
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
    # OCAP implies community governance over data use — 'permitted' with no
    # qualifications contradicts the governance intent.
    sovereignty = card.get("sovereignty") or {}
    frameworks = sovereignty.get("frameworks", [])
    if "OCAP" in frameworks and training == "permitted":
        errors.append(
            f"{card_id}: sovereignty.frameworks includes 'OCAP' but "
            f"usageRestrictions.training='permitted' — OCAP-governed data "
            f"should have community-asserted training restrictions."
        )

    # Rule 3: Active secretTest requires stewardship with ≥5 stewards.
    # The schema enforces this conditionally, but we double-check here
    # because the build should fail loudly, not silently.
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


def main():
    if not CARDS_DIR.exists():
        print(f"ERROR: Cards directory not found: {CARDS_DIR}")
        sys.exit(1)

    # Load all eval-type cards
    cards = []
    for card_path in sorted(CARDS_DIR.glob("eval-*.json")):
        try:
            card = json.loads(card_path.read_text(encoding="utf-8"))
            if card.get("type") == "eval":
                cards.append(card)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  WARN Skipping {card_path.name}: {e}")

    print(f"Found {len(cards)} eval cards in {CARDS_DIR}")

    # Validate sovereignty consistency rules
    all_errors = []
    for card in cards:
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

    # Build registry
    registry = {
        "registry_version": "2.1.0",
        "_generated": "Built from cli/shared/corpora-cards/ by build_registry.py. DO NOT EDIT — edit the cards instead.",
        "datasets": [card_to_registry_entry(c) for c in cards]
    }

    output = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"

    if SHOW_DIFF and REGISTRY_PATH.exists():
        import difflib
        old = REGISTRY_PATH.read_text(encoding="utf-8").splitlines()
        new = output.splitlines()
        diff = difflib.unified_diff(old, new, fromfile="registry.json (current)", tofile="registry.json (rebuilt)", lineterm="")
        diff_lines = list(diff)
        if diff_lines:
            print("\n".join(diff_lines))
        else:
            print("No changes.")
        return

    if DRY_RUN:
        print(f"Would write {len(registry['datasets'])} entries to {REGISTRY_PATH}")
        print(f"Preview (first entry):")
        if registry["datasets"]:
            print(json.dumps(registry["datasets"][0], indent=2))
        return

    REGISTRY_PATH.write_text(output, encoding="utf-8")
    print(f"Wrote {len(registry['datasets'])} entries to {REGISTRY_PATH}")


if __name__ == "__main__":
    main()
