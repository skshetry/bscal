"""Shared CLI helpers."""

import argparse
from collections.abc import Sequence


class _VersionAction(argparse.Action):
    """Like action="version", but resolve the version only when requested.

    importlib.metadata is slow to import and to query, and would otherwise
    dominate the startup time of every invocation.
    """

    def __init__(self, option_strings: Sequence[str], dest: str) -> None:
        super().__init__(
            option_strings,
            dest,
            nargs=0,
            default=argparse.SUPPRESS,
            help="show program's version number and exit",
        )

    def __call__(self, parser: argparse.ArgumentParser, *args: object) -> None:
        from importlib.metadata import PackageNotFoundError, version

        try:
            v = version("bscal")
        except PackageNotFoundError:
            v = "(unknown)"
        print(f"{parser.prog} {v}")
        parser.exit()


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
    parser.add_argument("--version", action=_VersionAction)
    return parser
