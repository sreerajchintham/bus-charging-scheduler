"""Pytest CLI that disables third-party plugin autoload (Conda/langsmith safe)."""

from __future__ import annotations

import os
import sys


def main() -> None:
    # Must be set before pytest imports plugin entry points.
    os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    from pytest import console_main

    raise SystemExit(console_main())


if __name__ == "__main__":
    main()
