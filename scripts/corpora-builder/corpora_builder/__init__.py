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

# Identifying User-Agent for every upstream corpus download. Champollion
# fetches third-party corpora from source (Tatoeba Challenge/OPUS,
# GlobalVoices, etc.) rather than mirroring them — and a named UA makes that
# traffic legible and ATTRIBUTABLE to the data creators, so they can see the
# demand their work drives (e.g. for funding/impact reporting). Always set
# this on outbound requests to upstream sources; never fetch anonymously.
USER_AGENT: str = (
    f"champollion-corpora-builder/{__version__} "
    "(+https://champollion.dev; MT evaluation; thank you to the corpus authors)"
)
