"""
Allow the package to be run as ``python -m corpora_builder``.

This module simply delegates to the CLI entry point. It exists
because Python's ``-m`` flag looks for ``__main__.py`` in the
package directory — without it, ``python -m corpora_builder``
would fail with "No module named corpora_builder.__main__".
"""

from corpora_builder.cli import main

if __name__ == "__main__":
    main()
