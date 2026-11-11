"""Shared CLI helpers."""

import argparse

try:
    from ._version import version
except ImportError:  # a source checkout that was never built or installed
    version = "(unknown)"


def should_use_color() -> bool:
    """Honor NO_COLOR > FORCE_COLOR > TERM=dumb > isatty (Python convention)."""
    import os
    import sys

    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("TERM") == "dumb":
        return False
    return sys.stdout.isatty()


def make_parser(epilog: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {version}")
    return parser
