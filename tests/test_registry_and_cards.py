"""Tests for dataset registry and method card features (v2.1)."""

import json
import tempfile
from pathlib import Path

import pytest

from mt_eval_harness.config import (
    load_registry,
    resolve_dataset,
    format_registry_table,
    load_method_card,
    validate_method_card,
    VALID_METHOD_CLASSES,
)


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestLoadRegistry:
    """Test registry loading from disk."""

    def test_loads_bundled_registry(self):
        """The bundled registry.json should load without error."""
        registry = load_registry()
        assert "registry_version" in registry
        assert "datasets" in registry
        assert isinstance(registry["datasets"], list)

    def test_loads_custom_registry(self, tmp_path):
        """Loading from a custom path should work."""
        custom = tmp_path / "custom_registry.json"
        custom.write_text(json.dumps({
            "registry_version": "1.0.0",
            "datasets": [
                {"id": "test-ds", "name": "Test", "url": None, "access": "public"}
            ]
        }))
        registry = load_registry(custom)
        assert len(registry["datasets"]) == 1
        assert registry["datasets"][0]["id"] == "test-ds"

    def test_missing_registry_raises(self, tmp_path):
        """Loading a nonexistent registry should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_registry(tmp_path / "nonexistent.json")


class TestResolveDataset:
    """Test dataset resolution: local paths and registry IDs."""

    def test_local_path_returned_directly(self, tmp_path):
        """A path to an existing file should be returned as-is."""
        corpus = tmp_path / "corpus.json"
        corpus.write_text("[]")
        result = resolve_dataset(str(corpus))
        assert result == corpus

    def test_unknown_id_raises(self, tmp_path):
        """An unknown dataset ID should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found in registry"):
            resolve_dataset("nonexistent-dataset-xyz")

    def test_private_dataset_raises_valueerror(self):
        """A registry entry with url=null should raise ValueError."""
        # The bundled registry has edtekla-dev-v1 with url=null
        with pytest.raises(ValueError, match="private"):
            resolve_dataset("edtekla-dev-v1")

    def test_nonexistent_path_falls_through_to_registry(self):
        """A path that doesn't exist should be checked against the registry."""
        # This path doesn't exist and isn't a registry ID
        with pytest.raises(FileNotFoundError):
            resolve_dataset("/absolutely/nonexistent/path/data.json")

    def test_url_dataset_downloads(self, tmp_path, monkeypatch):
        """A registry entry with a URL should download and cache."""
        # Create a custom registry with a URL pointing to a local file
        source = tmp_path / "source_corpus.json"
        source.write_text('[{"id": 0, "source": "hello"}]')

        registry = tmp_path / "registry.json"
        registry.write_text(json.dumps({
            "registry_version": "1.0.0",
            "datasets": [{
                "id": "test-downloadable",
                "name": "Test",
                "url": f"file://{source}",
                "access": "public",
                "sha256": None,
            }]
        }))

        result = resolve_dataset("test-downloadable", registry_path=registry)
        assert result.exists()
        assert json.loads(result.read_text())[0]["source"] == "hello"


class TestFormatRegistryTable:
    """Test the human-readable registry table formatter."""

    def test_produces_output(self):
        """The bundled registry should produce a non-empty table."""
        table = format_registry_table()
        assert "Available Evaluation Datasets" in table
        assert "edtekla-dev-v1" in table

    def test_empty_registry(self, tmp_path):
        """An empty registry should produce a 'no datasets' message."""
        empty = tmp_path / "empty.json"
        empty.write_text(json.dumps({
            "registry_version": "1.0.0",
            "datasets": []
        }))
        table = format_registry_table(empty)
        assert "No datasets registered" in table


# ---------------------------------------------------------------------------
# Method card tests
# ---------------------------------------------------------------------------

VALID_CARD = {
    "method_id": "test-method-v1",
    "name": "Test Method v1",
    "class": "raw-llm",
}

FULL_CARD = {
    "method_id": "fst-gated-v8",
    "name": "FST-Gated Coached Translation v8",
    "class": "pipeline",
    "description": "LLM translation with morphological validation.",
    "author": "Test Author",
    "tools_used": ["FST analyzer", "dictionary"],
    "open_source": False,
    "prompt_published": False,
    "supported_pairs": ["eng>crk"],
}


class TestValidateMethodCard:
    """Test method card validation."""

    def test_valid_minimal_card(self):
        """A card with only required fields should pass."""
        assert validate_method_card(VALID_CARD) == []

    def test_valid_full_card(self):
        """A card with all fields should pass."""
        assert validate_method_card(FULL_CARD) == []

    def test_missing_method_id(self):
        errors = validate_method_card({"name": "X", "class": "raw-llm"})
        assert any("method_id" in e for e in errors)

    def test_missing_name(self):
        errors = validate_method_card({"method_id": "x", "class": "raw-llm"})
        assert any("name" in e for e in errors)

    def test_missing_class(self):
        errors = validate_method_card({"method_id": "x", "name": "X"})
        assert any("class" in e for e in errors)

    def test_invalid_method_id_format(self):
        """method_id with uppercase or spaces should fail."""
        card = {**VALID_CARD, "method_id": "Invalid ID"}
        errors = validate_method_card(card)
        assert any("kebab-case" in e for e in errors)

    def test_invalid_class(self):
        """An unknown class value should fail."""
        card = {**VALID_CARD, "class": "magic-wand"}
        errors = validate_method_card(card)
        assert any("Invalid class" in e for e in errors)

    def test_all_valid_classes_accepted(self):
        """Every class in the enum should pass validation."""
        for cls in VALID_METHOD_CLASSES:
            card = {**VALID_CARD, "class": cls}
            assert validate_method_card(card) == [], f"Class '{cls}' should be valid"

    def test_tools_used_must_be_list(self):
        card = {**VALID_CARD, "tools_used": "FST analyzer"}
        errors = validate_method_card(card)
        assert any("array" in e for e in errors)

    def test_open_source_must_be_bool(self):
        card = {**VALID_CARD, "open_source": "yes"}
        errors = validate_method_card(card)
        assert any("boolean" in e for e in errors)


class TestLoadMethodCard:
    """Test loading method cards from disk."""

    def test_loads_valid_card(self, tmp_path):
        """A valid method card file should load successfully."""
        path = tmp_path / "method.json"
        path.write_text(json.dumps(FULL_CARD))
        card = load_method_card(path)
        assert card["method_id"] == "fst-gated-v8"
        assert card["class"] == "pipeline"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_method_card(tmp_path / "nonexistent.json")

    def test_invalid_card_raises_valueerror(self, tmp_path):
        """A card with missing required fields should raise ValueError."""
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"method_id": "x"}))
        with pytest.raises(ValueError, match="Invalid method card"):
            load_method_card(path)
