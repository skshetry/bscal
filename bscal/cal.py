import calendar
from collections.abc import Iterator, Sequence
from enum import IntEnum

from . import BSDate, bs_to_ad, lookup


class Month(IntEnum):
    BAISAKH = 1
    JESTHA = 2
    ASADH = 3
    SHRAWAN = 4
    BHADRA = 5
    ASOJ = 6
    KARTIK = 7
    MANGSIR = 8
    POUSH = 9
    MAGH = 10
    FALGUN = 11
    CHAITRA = 12


(
    BAISAKH,
    JESTHA,
    ASADH,
    SHRAWAN,
    BHADRA,
    ASOJ,
    KARTIK,
    MANGSIR,
    POUSH,
    MAGH,
    FALGUN,
    CHAITRA,
) = Month


# 1-indexed BS month names, mirroring stdlib calendar.month_name. Derived from
# the Month enum so the enum is the single source of truth for BS month names.
month_name = ("", *(m.name.title() for m in Month))
month_abbr = ("", *(m.name[:3].title() for m in Month))


class BSCalendar(calendar.TextCalendar):
    def formatmonthname(
        self, theyear: int, themonth: int, width: int, withyear: bool = True
    ) -> str:
        """Return a formatted BS month name."""
        s = month_name[themonth]
        if withyear:
            s = f"{s} {theyear}"
        return s.center(width)

    def itermonthdays(self, year: int, month: int) -> Iterator[int]:
        """Like itermonthdates(), but yields day numbers (0 outside month)."""
        day1, ndays = monthrange(year, month)
        days_before = (day1 - self.firstweekday) % 7
        days_after = (self.firstweekday - day1 - ndays) % 7
        yield from [0] * days_before
        yield from range(1, ndays + 1)
        yield from [0] * days_after


class _CLICalendar(BSCalendar):
    def __init__(
        self,
        highlight_day: tuple[int, int, int] | None = None,
        firstweekday: int = 0,
    ) -> None:
        super().__init__(firstweekday)
        self.highlight_day = highlight_day

    def monthdays2calendar(  # type: ignore[override]  # ty: ignore[invalid-method-override]
        self, year: int, month: int
    ) -> list[list[tuple[int, int, int, int]]]:
        # Widen each cell with (year, month) so formatweek can highlight the
        # right day in year view, where weeks from 12 months are interleaved.
        # Assumes stdlib only unpacks cells inside formatweek (which we override).
        weeks = super().monthdays2calendar(year, month)
        return [[(d, wd, year, month) for (d, wd) in week] for week in weeks]

    def formatweek(  # type: ignore[override]  # ty: ignore[invalid-method-override]
        self, theweek: list[tuple[int, int, int, int]], width: int
    ) -> str:
        return " ".join(
            self._formatday(d, wd, width, year, month)
            for (d, wd, year, month) in theweek
        )

    def _formatday(
        self, day: int, weekday: int, width: int, year: int, month: int
    ) -> str:
        s = self.formatday(day, weekday, width)
        if self.highlight_day and day and self.highlight_day == (year, month, day):
            return f"\033[30;43m{s}\033[0m"
        return s


def isleap(year: int) -> bool:
    """Return True if `year` is a 366-day BS year."""
    return sum(lookup[year]) == 366  # noqa: PLR2004


def leapdays(y1: int, y2: int) -> int:
    """Return the number of BS leap years in [y1, y2)."""
    return sum(1 for y in range(y1, y2) if isleap(y))


def weekday(year: int, month: int, day: int) -> int:
    """Return weekday (Mon=0..Sun=6) of BS year/month/day."""
    return bs_to_ad(year, month, day).weekday()


def monthrange(year: int, month: int) -> tuple[int, int]:
    """Return (weekday_of_1st, days_in_month) for BS year/month."""
    return weekday(year, month, 1), lookup[year][month - 1]


def main(args: Sequence[str] | None = None) -> None:
    from ._cli import _should_use_color, make_parser

    parser = make_parser(
        epilog=(
            "examples:\n"
            "  bscal              current month\n"
            "  bscal 2080         year 2080 (year-view)\n"
            "  bscal 2080 9       Poush 2080 (month-view)\n"
        ),
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=2,
        help="width of date column (default 2)",
    )
    parser.add_argument(
        "-l",
        "--lines",
        type=int,
        default=1,
        help="number of lines per week (default 1)",
    )
    parser.add_argument(
        "-s",
        "--spacing",
        type=int,
        default=6,
        help="spacing between months in year view (default 6)",
    )
    parser.add_argument(
        "-m",
        "--months",
        type=int,
        default=3,
        help="months per row in year view (default 3)",
    )
    parser.add_argument(
        "-f",
        "--first-weekday",
        type=int,
        default=6,
        help="first day of week, 0=Mon..6=Sun (default 6)",
    )
    parser.add_argument(
        "year",
        nargs="?",
        type=int,
        help=f"year number ({BSDate.min.year}-{BSDate.max.year})",
    )
    parser.add_argument("month", nargs="?", type=int, help="month number (1-12)")
    opts = parser.parse_args(args)
    if opts.year is not None and not BSDate.min.year <= opts.year <= BSDate.max.year:
        parser.error(f"year {opts.year} outside [{BSDate.min.year}, {BSDate.max.year}]")
    if opts.month is not None and not 1 <= opts.month <= 12:  # noqa: PLR2004
        parser.error(f"month {opts.month} outside [1, 12]")
    if not 0 <= opts.first_weekday <= 6:  # noqa: PLR2004
        parser.error(f"first-weekday {opts.first_weekday} outside [0, 6]")
    today = BSDate.today()
    cal = _CLICalendar(
        (today.year, today.month, today.day) if _should_use_color() else None,
        opts.first_weekday,
    )
    if not opts.year or opts.month:
        result = cal.formatmonth(
            opts.year or today.year,
            opts.month or today.month,
            w=opts.width,
            l=opts.lines,
        )
    else:
        result = cal.formatyear(
            opts.year,
            w=opts.width,
            l=opts.lines,
            c=opts.spacing,
            m=opts.months,
        )
    print(result)


if __name__ == "__main__":
    main()
