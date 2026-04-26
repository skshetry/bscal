"""Shared CLI helpers."""

import argparse


def _version_string() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return f"%(prog)s {version('bscal')}"
    except PackageNotFoundError:
        return "%(prog)s (unknown)"


def _should_use_color() -> bool:
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
    parser.add_argument("--version", action="version", version=_version_string())
    return parser
