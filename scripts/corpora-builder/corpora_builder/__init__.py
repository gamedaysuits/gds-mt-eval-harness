"""
Champollion Corpora Builder
============================

Multi-source corpus construction tooling for the MT Eval Arena.

Imports human-authored parallel text from public sources, classifies each
entry by domain and difficulty, and outputs structured corpus JSON files
ready for evaluation.
"""

# Single source of truth for the package version.
# Kept here rather than read from importlib.metadata so the version is
# available in editable installs and before formal packaging.
__version__: str = "0.1.0"
