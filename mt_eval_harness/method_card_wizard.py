"""
Method Card Wizard — Interactive CLI wizard for creating method cards.

Triggered during 'mt-eval publish' when no --method-card is provided
and auto_confirm is False. Walks the user through defining their
method's metadata for reproducibility and attribution.

A method card is the identity document of an evaluation run. It answers:
    "What method produced these translations?"

The wizard produces a dict that matches the method.json manifest format,
making it compatible with both inline publish metadata and standalone
method plugin directories.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


# Default method classes — presented as a numbered menu.
# These align with the categories defined in BENCHMARK_SPEC §2.
METHOD_CLASSES = [
    ("raw-llm", "Raw LLM — Direct API call, minimal instruction"),
    ("coached-llm", "Coached LLM — LLM with coaching prompt / few-shot"),
    ("pipeline", "Pipeline — Multi-stage processing (decomp-recomp, etc.)"),
    ("api", "API — External translation service (Google, DeepL, etc.)"),
    ("fine-tuned", "Fine-tuned — Custom fine-tuned model"),
    ("human", "Human — Human translation baseline"),
]


def _slugify(name: str) -> str:
    """Convert a method name to a kebab-case slug.

    Example: 'CRK Coached v8.2' → 'crk-coached-v8-2'
    """
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def run_wizard(submitter: str = "") -> dict | None:
    """Run the interactive method card wizard.

    Args:
        submitter: Pre-filled author name (from OAuth identity).

    Returns:
        Method card dict, or None if the user cancels.
    """
    print("\n" + "─" * 50)
    print("  Method Card Wizard")
    print("  A method card identifies what produced your translations.")
    print("─" * 50)

    # --- Method name ---
    print("\n  1. Method Name")
    print("     Examples: 'GPT-4o Naive', 'CRK Coached v8.2',")
    print("               'DeepL API', 'Decomp-Recomp Pipeline'")
    name = input("\n     Name: ").strip()
    if not name:
        print("     Cancelled (no name provided).")
        return None

    # --- Method ID ---
    default_id = _slugify(name)
    print(f"\n  2. Method ID (kebab-case, used as unique identifier)")
    method_id = input(f"     ID [{default_id}]: ").strip() or default_id

    # --- Method class ---
    print("\n  3. Method Class")
    for i, (class_id, description) in enumerate(METHOD_CLASSES, 1):
        print(f"     {i}. {description}")

    class_input = input("\n     Class [1]: ").strip() or "1"
    try:
        class_idx = int(class_input) - 1
        if 0 <= class_idx < len(METHOD_CLASSES):
            method_class = METHOD_CLASSES[class_idx][0]
        else:
            method_class = "raw-llm"
    except ValueError:
        # Allow freeform class input (e.g., "custom-type")
        method_class = class_input

    # --- Author ---
    print(f"\n  4. Author")
    author = input(f"     Author [{submitter or 'anonymous'}]: ").strip()
    if not author:
        author = submitter or "anonymous"

    # --- Description ---
    print(f"\n  5. Description (optional, press Enter to skip)")
    description = input("     Description: ").strip()

    # --- Build the card ---
    card = {
        "name": name,
        "method_id": method_id,
        "class": method_class,
        "author": author,
    }
    if description:
        card["description"] = description

    # --- Preview ---
    print("\n" + "─" * 50)
    print("  Method Card Preview:")
    for key, value in card.items():
        print(f"    {key}: {value}")
    print("─" * 50)

    # --- Confirm ---
    confirm = input("\n  Use this method card? [Y/n] ").strip().lower()
    if confirm and confirm != "y":
        print("  Cancelled.")
        return None

    # --- Offer to save ---
    save = input("  Save to method_card.json for reuse? [y/N] ").strip().lower()
    if save == "y":
        save_path = Path("method_card.json")
        save_path.write_text(
            json.dumps(card, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"  Saved to {save_path.resolve()}")
        print(f"  Reuse with: mt-eval publish --method-card {save_path}")

    return card
