"""Calendar functions for Bikram Sambat, mirroring the stdlib calendar module."""

import calendar
from collections.abc import Iterator, Sequence
from enum import IntEnum

from . import BSDate, _check_year, bs_to_ad, lookup, months


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


# 1-indexed BS month names, mirroring stdlib calendar.month_name/month_abbr.
month_name = ("", *months)
month_abbr = ("", *(name[:3] for name in months))


def _monthlen(year: int, month: int) -> int:
    _check_year(year)
    return lookup[year][month - 1]


def isleap(year: int) -> bool:
    """Return True if `year` is a 366-day BS year."""
    _check_year(year)
    return sum(lookup[year]) == 366  # noqa: PLR2004


def leapdays(y1: int, y2: int) -> int:
    """Return the number of BS leap years in [y1, y2)."""
    return sum(1 for y in range(y1, y2) if isleap(y))


def weekday(year: int, month: int, day: int) -> int:
    """Return weekday (Mon=0..Sun=6) of BS year/month/day."""
    return bs_to_ad(year, month, day).weekday()


def monthrange(year: int, month: int) -> tuple[int, int]:
    """Return (weekday_of_1st, days_in_month) for BS year/month."""
    return weekday(year, month, 1), _monthlen(year, month)


class BSCalendar(calendar.TextCalendar):
    def formatmonthname(
        self, theyear: int, themonth: int, width: int, withyear: bool = True
    ) -> str:
        """Return a formatted BS month name."""
        s = month_name[themonth]
        if withyear:
            s = f"{s} {theyear}"
        return s.center(width)

    def _padding(self, year: int, month: int) -> tuple[int, int, int]:
        """Return (days_before, days_in_month, days_after) for the month's grid.

        The grid shows whole weeks starting on self.firstweekday, so the days
        before and after the month fill its first and last week.
        """
        day1, ndays = monthrange(year, month)
        days_before = (day1 - self.firstweekday) % 7
        days_after = (self.firstweekday - day1 - ndays) % 7
        return days_before, ndays, days_after

    def itermonthdays(self, year: int, month: int) -> Iterator[int]:
        """Like itermonthdates(), but yields day numbers (0 outside month)."""
        days_before, ndays, days_after = self._padding(year, month)
        yield from [0] * days_before
        yield from range(1, ndays + 1)
        yield from [0] * days_after

    def itermonthdays3(self, year: int, month: int) -> Iterator[tuple[int, int, int]]:
        """Like itermonthdates(), but yields BS (year, month, day) tuples.

        Raises ValueError if the padding days fall in a year outside the
        supported range, as their month lengths are unknown.
        """
        days_before, ndays, days_after = self._padding(year, month)
        if days_before:  # the last days of the previous month
            y, m = (year, month - 1) if month > BAISAKH else (year - 1, CHAITRA)
            end = _monthlen(y, m) + 1  # also rejects years outside the table
            for d in range(end - days_before, end):
                yield y, m, d
        for d in range(1, ndays + 1):
            yield year, month, d
        if days_after:  # the first days of the next month
            y, m = (year, month + 1) if month < CHAITRA else (year + 1, BAISAKH)
            _check_year(y)  # day numbers need no table, but the year must exist
            for d in range(1, days_after + 1):
                yield y, m, d

    def itermonthdates(  # type: ignore[override]  # ty: ignore[invalid-method-override]
        self, year: int, month: int
    ) -> Iterator[BSDate]:
        """Like the stdlib method, but yields BSDate values.

        BSDate is not a datetime.date subclass, so this deliberately narrows
        the stdlib return type. The inherited monthdatescalendar() and
        yeardatescalendar() call this method, so they return BSDate values too.
        """
        for y, m, d in self.itermonthdays3(year, month):
            yield BSDate(y, m, d)


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
            self._formatcell(d, wd, width, year, month)
            for (d, wd, year, month) in theweek
        )

    def _formatcell(
        self, day: int, weekday: int, width: int, year: int, month: int
    ) -> str:
        """formatday(), highlighted if (year, month, day) is highlight_day."""
        s = self.formatday(day, weekday, width)
        if self.highlight_day == (year, month, day):
            return f"\033[30;43m{s}\033[0m"
        return s


def main(args: Sequence[str] | None = None) -> None:
    from ._cli import make_parser, should_use_color

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
    if opts.month is not None and not BAISAKH <= opts.month <= CHAITRA:
        parser.error(f"month {opts.month} outside [1, 12]")
    if not calendar.MONDAY <= opts.first_weekday <= calendar.SUNDAY:
        parser.error(f"first-weekday {opts.first_weekday} outside [0, 6]")
    if opts.months < 1:
        parser.error(f"months {opts.months} must be at least 1")
    today = BSDate.today()
    highlight_day = (today.year, today.month, today.day)
    cal = _CLICalendar(
        highlight_day=highlight_day if should_use_color() else None,
        firstweekday=opts.first_weekday,
    )
    if opts.year is not None and opts.month is None:  # `bscal 2080`
        result = cal.formatyear(
            opts.year, w=opts.width, l=opts.lines, c=opts.spacing, m=opts.months
        )
    else:  # `bscal` or `bscal 2080 9`
        result = cal.formatmonth(
            opts.year or today.year,
            opts.month or today.month,
            w=opts.width,
            l=opts.lines,
        )
    print(result)


if __name__ == "__main__":
    main()
