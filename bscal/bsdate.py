"""bsdate: like date(1), but shows the date in Bikram Sambat."""

from collections.abc import Sequence
from datetime import date, datetime, timezone, tzinfo

from . import BSDate, _bs_strftime

# -I[FMT] formats for BS dates, matching GNU and BSD date (offset as +hh:mm).
_ISO_FORMATS = {
    "date": "%Y-%m-%d",
    "hours": "%Y-%m-%dT%H%:z",
    "minutes": "%Y-%m-%dT%H:%M%:z",
    "seconds": "%Y-%m-%dT%H:%M:%S%:z",
}
_DEFAULT_AD_FORMAT = "%a %b %e %T %Z %Y"  # like date(1)
_DEFAULT_BS_FORMAT = "%a %B %-d %T %Z %Y"


def _parse_ad_datetime(date_str: str | None, tz: tzinfo | None) -> datetime:
    """Parse DATE: an ISO date or datetime, or @<unix-timestamp>; None is now.

    A date without a time gets the current time of day. Input without an
    offset is in `tz`, or naive local time if `tz` is None.
    """
    if not date_str:
        return datetime.now(tz)
    if date_str.startswith("@"):
        return datetime.fromtimestamp(int(date_str[1:]), tz)
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        dt = datetime.fromisoformat(date_str)
    else:
        dt = datetime.combine(d, datetime.now(tz).time())
    if dt.tzinfo is None and tz is not None:
        dt = dt.replace(tzinfo=tz)
    return dt


def _bs_to_ad_datetime(bs_datestring: str, *, utc: bool) -> datetime:
    """Return the AD datetime of a BS date string, at the current time of day."""
    tz = timezone.utc if utc else None
    ad = BSDate.fromisoformat(bs_datestring).to_ad()
    ad_dt = datetime.combine(ad, datetime.now(tz).time(), tzinfo=tz)
    return ad_dt if utc else ad_dt.astimezone()


def _format_ad(ad_dt: datetime, user_format: str | None, iso_fmt: str | None) -> str:
    if iso_fmt == "date":
        return ad_dt.date().isoformat()
    if iso_fmt is not None:  # "hours", "minutes" or "seconds"
        return ad_dt.isoformat(timespec=iso_fmt)
    return ad_dt.strftime(user_format or _DEFAULT_AD_FORMAT)


def bsconv(bs_datestring: str, iso: bool = False) -> None:
    """Print the AD date of a BS date string."""
    ad_dt = _bs_to_ad_datetime(bs_datestring, utc=False)
    print(_format_ad(ad_dt, None, "date" if iso else None))


def _split_date_args(
    argv: Sequence[str],
) -> tuple[str | None, str | None, list[str]]:
    """Split off date(1)-style "+FORMAT" and "-I[FMT]" arguments.

    argparse cannot parse these: "+FORMAT" is not an option, and "-I" takes
    a value only when attached ("-Iseconds"), so "-I 2024-04-13" must leave
    the date as a positional. As in date(1), options end at "--", but a
    "+FORMAT" after it still counts.

    Return (user_format, iso_fmt, remaining_args).
    """
    user_format: str | None = None
    iso_fmt: str | None = None
    rest: list[str] = []
    options_done = False
    for arg in argv:
        if user_format is None and arg.startswith("+"):
            user_format = arg[1:]
        elif options_done:
            rest.append(arg)
        elif arg == "--":
            options_done = True
            rest.append(arg)
        elif arg in ("-I", "--iso-8601"):
            iso_fmt = "date"
        elif arg.startswith("--iso-8601="):
            iso_fmt = arg.removeprefix("--iso-8601=")
        elif arg.startswith("-I"):
            iso_fmt = arg.removeprefix("-I")
        else:
            rest.append(arg)
    return user_format, iso_fmt, rest


def _print_date(
    date_str: str | None,
    convert: str | None,
    user_format: str | None,
    iso_fmt: str | None,
    *,
    utc: bool,
) -> None:
    if convert is not None:
        print(_format_ad(_bs_to_ad_datetime(convert, utc=utc), user_format, iso_fmt))
        return

    # As in date(1), -u applies to the input too: DATE without an offset is UTC.
    dt = _parse_ad_datetime(date_str, timezone.utc if utc else None)
    if utc:
        dt = dt.astimezone(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.astimezone()
    bd = BSDate.from_ad(dt)
    fmt = _ISO_FORMATS[iso_fmt] if iso_fmt is not None else user_format
    print(_bs_strftime(fmt or _DEFAULT_BS_FORMAT, bd, dt))


def main(args: Sequence[str] | None = None) -> None:
    import sys

    from ._cli import make_parser

    user_format, iso_fmt, rest = _split_date_args(
        sys.argv[1:] if args is None else args
    )
    parser = make_parser(
        epilog=(
            "examples:\n"
            "  bsdate                       show today in BS\n"
            "  bsdate 2024-04-13            AD date to BS\n"
            "  bsdate 2024-04-13T12:00      AD datetime to BS\n"
            "  bsdate @1700000000           unix timestamp to BS\n"
            "  bsdate -c 2081-01-01         BS date to AD\n"
            "  bsdate -I 2024-04-13         BS date in ISO 8601 (date)\n"
            "  bsdate -Iseconds             BS now, ISO 8601 with seconds\n"
            "  bsdate +'%Y-%m-%d %B'        custom strftime (BS-aware)\n"
            "  bsdate -u                    show today in BS (UTC)\n"
            "\n"
            "ISO formats (-I[FMT] or --iso-8601[=FMT]): "
            + ", ".join(_ISO_FORMATS)
            + "\n"
            "BS-aware strftime tokens: %Y %y %C %m %d %e %B %b %h %j %F %D %x %c.\n"
            "%:z prints the time zone offset as +hh:mm.\n"
            "Avoid %G %g %U %V %W — week tokens stay Gregorian-anchored.\n"
            "Unsupported tokens are printed as is.\n"
        ),
    )
    parser.add_argument(
        "-u",
        "--utc",
        "--universal",
        action="store_true",
        help="display in UTC instead of local time",
    )
    parser.add_argument(
        "-c",
        "--from-bs",
        metavar="<bs_date>",
        dest="convert",
        help="convert BS date (YYYY-M-D) to AD",
    )
    parser.add_argument(
        "date",
        nargs="?",
        metavar="DATE",
        help="datetime string in isoformat, or @<unix-timestamp>",
    )
    opts = parser.parse_args(rest)

    if iso_fmt is not None and iso_fmt not in _ISO_FORMATS:
        parser.error(
            f"invalid ISO format {iso_fmt!r} (choose from {', '.join(_ISO_FORMATS)})"
        )
    if user_format is not None and iso_fmt is not None:
        parser.error("+FORMAT and -I/--iso-8601 are mutually exclusive")
    if opts.convert is not None and opts.date is not None:
        parser.error("-c/--from-bs and DATE are mutually exclusive")

    try:
        _print_date(opts.date, opts.convert, user_format, iso_fmt, utc=opts.utc)
    except (ValueError, OverflowError, OSError) as e:
        # Bad dates, timestamps, or TZ settings: report them like argparse does.
        parser.error(str(e))


if __name__ == "__main__":
    main()
