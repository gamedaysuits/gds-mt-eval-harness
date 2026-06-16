"""
Source adapters for the corpora builder.

Each adapter implements the SourceAdapter ABC to fetch parallel text
from a specific data source (Tatoeba, OPUS, CSV, etc.).

Adapters are imported explicitly by name rather than auto-discovered,
because we want the dependency graph to stay obvious and predictable.
"""
