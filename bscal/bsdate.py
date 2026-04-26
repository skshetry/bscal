from collections.abc import Sequence
from datetime import date, datetime, timezone

from . import BSDate

_ISO_FORMATS = {
    "date": "%Y-%m-%d",
    "hours": "%Y-%m-%dT%H%z",
    "minutes": "%Y-%m-%dT%H:%M%z",
    "seconds": "%Y-%m-%dT%H:%M:%S%z",
}


def _resolve_dt(date_str: str | None) -> datetime:
    if not date_str:
        return datetime.now()
    if date_str.startswith("@"):
        return datetime.fromtimestamp(int(date_str[1:]))
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        return datetime.fromisoformat(date_str)
    return datetime.combine(d, datetime.now().time())


def bsconv(bs_datestring: str, iso: bool = False) -> None:
    ad = BSDate.fromisoformat(bs_datestring).to_ad()
    if iso:
        print(ad.isoformat())
        return
    ad_tz = datetime.combine(ad, datetime.now().time()).astimezone()
    print(ad_tz.strftime("%a %b %e %T %Z %Y"))


def main(args: Sequence[str] | None = None) -> None:  # noqa: C901, PLR0912, PLR0915
    import sys

    from . import _bs_strftime
    from ._cli import make_parser
    from .cal import month_name

    raw = list(args) if args is not None else sys.argv[1:]
    user_format: str | None = None
    iso_fmt: str | None = None
    cleaned: list[str] = []
    for a in raw:
        if user_format is None and a.startswith("+"):
            user_format = a[1:]
            continue
        if a in ("-I", "--iso-8601"):
            iso_fmt = "date"
            continue
        if a.startswith("--iso-8601="):
            iso_fmt = a[len("--iso-8601=") :]
            continue
        if a.startswith("-I") and len(a) > 2:  # noqa: PLR2004
            iso_fmt = a[2:]
            continue
        cleaned.append(a)

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
            "BS-aware strftime tokens: %Y %y %C %m %d %e %B %b %h %j %F %D.\n"
            "Avoid %G %g %U %V %W — week tokens stay Gregorian-anchored.\n"
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
    opt = parser.parse_args(cleaned)

    if iso_fmt is not None and iso_fmt not in _ISO_FORMATS:
        parser.error(
            f"invalid ISO format {iso_fmt!r} (choose from {', '.join(_ISO_FORMATS)})"
        )
    if user_format is not None and iso_fmt:
        parser.error("+FORMAT and -I/--iso-8601 are mutually exclusive")

    if opt.convert:
        ad = BSDate.fromisoformat(opt.convert).to_ad()
        ad_dt = datetime.combine(
            ad,
            datetime.now(timezone.utc if opt.utc else None).time(),
            tzinfo=timezone.utc if opt.utc else None,
        )
        if not opt.utc:
            ad_dt = ad_dt.astimezone()
        if user_format is not None:
            print(ad_dt.strftime(user_format))
        elif iso_fmt:
            print(ad_dt.strftime(_ISO_FORMATS[iso_fmt]))
        else:
            print(ad_dt.strftime("%a %b %e %T %Z %Y"))
        return

    dt = _resolve_dt(opt.date)
    if opt.utc:
        dt = dt.astimezone(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.astimezone()
    bd = BSDate.from_ad(dt.date())

    if user_format is not None:
        print(_bs_strftime(user_format, dt, bd.year, bd.month, bd.day))
    elif iso_fmt:
        print(_bs_strftime(_ISO_FORMATS[iso_fmt], dt, bd.year, bd.month, bd.day))
    else:
        print(
            dt.strftime("%a"),
            month_name[bd.month],
            bd.day,
            dt.strftime("%T %Z"),
            bd.year,
        )


if __name__ == "__main__":
    main()
