"""Shared test fixtures for mt-eval-harness."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a clean temporary directory."""
    return tmp_path


@pytest.fixture
def sample_corpus(tmp_path):
    """Create a minimal corpus JSON file for testing.

    Uses the default 'source'/'target' field names so tests work
    zero-config — no --source-field override needed.
    """
    corpus = [
        {"id": 0, "source": "Hello.", "target": "Bonjour.", "segment": "basic", "difficulty": 1},
        {"id": 1, "source": "Thank you.", "target": "Merci.", "segment": "basic", "difficulty": 1},
        {"id": 2, "source": "I see a dog.", "target": "Je vois un chien.", "segment": "intermediate", "difficulty": 2},
        {"id": 3, "source": "She is running.", "target": "Elle court.", "segment": "intermediate", "difficulty": 2},
        {"id": 4, "source": "The sky is blue.", "target": "Le ciel est bleu.", "segment": "advanced", "difficulty": 3},
    ]
    corpus_path = tmp_path / "corpus.json"
    corpus_path.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf-8")
    return str(corpus_path)


@pytest.fixture
def custom_field_corpus(tmp_path):
    """Create a corpus with non-default field names (simulates Cree-style corpus).

    This tests the --source-field / --target-field override mechanism.
    """
    corpus = [
        {"id": 0, "english": "Hello.", "cree_sro": "tânisi.", "segment": "basic"},
        {"id": 1, "english": "Thank you.", "cree_sro": "kinanâskomitin.", "segment": "basic"},
    ]
    corpus_path = tmp_path / "custom_corpus.json"
    corpus_path.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf-8")
    return str(corpus_path)


@pytest.fixture
def sample_run_log():
    """Create a minimal RunLog dict matching the new schema.

    Uses 'source' key (not 'english') to validate the schema rename.
    """
    return {
        "run_id": "test_run_001",
        "config": {
            "model": "test-model",
            "source_field": "source",
            "target_field": "target",
        },
        "results": [
            {
                "id": 0,
                "source": "Hello.",
                "expected": "Bonjour.",
                "predicted": "Bonjour.",
                "segment": "basic",
                "difficulty": 1,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 100, "completion_tokens": 10},
                "cost_usd": 0.001,
                "tool_calls": [],
                "tool_call_count": 0,
                "error": None,
                "metadata": {},
            },
            {
                "id": 1,
                "source": "Thank you.",
                "expected": "Merci.",
                "predicted": "Merci beaucoup.",
                "segment": "basic",
                "difficulty": 1,
                "latency_s": 0.3,
                "usage": {"prompt_tokens": 80, "completion_tokens": 8},
                "cost_usd": 0.0008,
                "tool_calls": [],
                "tool_call_count": 0,
                "error": None,
                "metadata": {},
            },
        ],
    }
