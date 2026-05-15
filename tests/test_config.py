"""Tests for RunConfig defaults and validation.

Validates that the config module enforces language-agnostic defaults:
    - source_field defaults to 'source' (not 'english')
    - target_field defaults to 'target' (not 'cree_sro')
    - segment_names defaults to empty list (auto-detected from corpus)
    - max_tokens defaults to a reasonable general-purpose value
"""

from mt_eval_harness.config import RunConfig


class TestRunConfigDefaults:
    """Verify defaults enforce language-agnostic behavior."""

    def test_source_field_default_is_source(self):
        """The source_field must default to 'source', not 'english'."""
        config = RunConfig()
        assert config.source_field == "source"

    def test_target_field_default_is_target(self):
        """The target_field must default to 'target', not any language-specific name."""
        config = RunConfig()
        assert config.target_field == "target"

    def test_segment_names_default_empty(self):
        """Segment names should default to empty list for auto-detection."""
        config = RunConfig()
        assert config.segment_names == []

    def test_max_tokens_reasonable(self):
        """max_tokens should be a general-purpose value, not Cree-specific 13680."""
        config = RunConfig()
        assert config.max_tokens == 4096

    def test_dataset_default_all(self):
        config = RunConfig()
        assert config.dataset == "all"

    def test_batch_size_default_one(self):
        config = RunConfig()
        assert config.batch_size == 1


class TestRunConfigOverrides:
    """Verify that custom field names work for non-default corpora."""

    def test_custom_source_field(self):
        config = RunConfig(source_field="english")
        assert config.source_field == "english"

    def test_custom_target_field(self):
        config = RunConfig(target_field="cree_sro")
        assert config.target_field == "cree_sro"

    def test_custom_segment_names(self):
        names = ["gold_standard", "textbook_sample"]
        config = RunConfig(segment_names=names)
        assert config.segment_names == names

    def test_custom_max_tokens(self):
        config = RunConfig(max_tokens=13680)
        assert config.max_tokens == 13680
