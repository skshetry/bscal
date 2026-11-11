"""Bikram Sambat (BS), the official calendar of Nepal.

BS month lengths (29-32 days) follow astronomical observation, not a
formula, so conversion is table-driven and only works for the years listed:

- ``lookup[year]``: the 12 month lengths of BS ``year``.
- ``new_years[year]``: the AD date of 1 Baisakh (BS new year's day) of ``year``,
  derived from ``lookup``.

Supported range: BS 1970-01-01 to 2100-12-30 (AD 1913-04-13 to 2044-04-12).
"""

import re
from bisect import bisect_right
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from itertools import accumulate, chain
from operator import index
from typing import ClassVar, overload

lookup = {
    # bs_year: [days_in_each_month, ...]
    1970: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1971: [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
    1972: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    1973: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    1974: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1975: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    1976: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    1977: [30, 32, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31],
    1978: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1979: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    1980: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    1981: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    1982: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1983: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    1984: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    1985: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    1986: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1987: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    1988: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    1989: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    1990: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1991: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    1992: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    1993: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    1994: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1995: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    1996: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    1997: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1998: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    1999: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2000: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2001: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2002: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2003: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2004: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2005: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2006: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2007: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2008: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
    2009: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2010: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2011: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2012: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2013: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2014: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2015: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2016: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2017: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2018: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2019: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2020: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2021: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2022: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2023: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2024: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2025: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2026: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2027: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2028: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2029: [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
    2030: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2031: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2032: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2033: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2034: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2035: [30, 32, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
    2036: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2037: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2038: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2039: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2040: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2041: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2042: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2043: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2044: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2045: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2046: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2047: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2048: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2049: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2050: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2051: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2052: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2053: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2054: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2055: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2056: [31, 31, 32, 31, 32, 30, 30, 29, 30, 29, 30, 30],
    2057: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2058: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2059: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2060: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2061: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2062: [30, 32, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31],
    2063: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2064: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2065: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2066: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 29, 31],
    2067: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2068: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2069: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2070: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2071: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2072: [31, 32, 31, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2073: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2074: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2075: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2076: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2077: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2078: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30],
    2079: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2080: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 30],
    2081: [31, 32, 31, 32, 31, 30, 30, 30, 29, 30, 29, 31],
    2082: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2083: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2084: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2085: [31, 32, 31, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2086: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2087: [31, 31, 32, 31, 31, 31, 30, 30, 29, 30, 30, 30],
    2088: [30, 31, 32, 32, 30, 31, 30, 30, 29, 30, 30, 30],
    2089: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2090: [30, 32, 31, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2091: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2092: [31, 31, 32, 32, 31, 30, 30, 30, 29, 30, 30, 30],
    2093: [31, 31, 31, 32, 31, 31, 29, 30, 29, 30, 29, 31],
    2094: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
    2095: [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
    2096: [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
    2097: [31, 31, 31, 32, 31, 31, 29, 30, 30, 29, 30, 30],
    2098: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
    2099: [31, 31, 32, 31, 31, 31, 30, 29, 29, 30, 30, 30],
    2100: [31, 32, 31, 32, 30, 31, 30, 29, 30, 29, 30, 30],
}

months = [
    "Baisakh",
    "Jestha",
    "Asadh",
    "Shrawan",
    "Bhadra",
    "Asoj",
    "Kartik",
    "Mangsir",
    "Poush",
    "Magh",
    "Falgun",
    "Chaitra",
]

_first_bs_year = min(lookup)
_last_bs_year = max(lookup)

# Ordinal (see date.toordinal) of the first day of every BS month in the table,
# in order, followed by one past the last supported day. Years are contiguous,
# so month m of year y is at index (y - _first_bs_year) * 12 + m - 1.
# Only the first day is a known date: BS 1970-01-01 is AD 1913-04-13. The rest
# follows from the month lengths in lookup.
_month_ordinals = list(
    accumulate(
        chain.from_iterable(lookup.values()), initial=date(1913, 4, 13).toordinal()
    )
)
new_years = {
    year: date.fromordinal(_month_ordinals[12 * i]) for i, year in enumerate(lookup)
}
_min_ad = date.fromordinal(_month_ordinals[0])
_max_ad = date.fromordinal(_month_ordinals[-1] - 1)


def _check_year(year: int) -> None:
    if index(year) not in lookup:
        raise ValueError(f"year {year} outside [{_first_bs_year}, {_last_bs_year}]")


def bs_to_ad(year: int, month: int, day: int) -> date:
    """Return the AD date of BS `year`-`month`-`day`.

    Raise TypeError if an argument is not an integer, and ValueError if the
    date is invalid or outside the supported range.
    """
    # Like datetime.date: non-integers are a TypeError, not a range error.
    year, month, day = index(year), index(month), index(day)
    _check_year(year)
    if not 1 <= month <= 12:  # noqa: PLR2004
        raise ValueError(f"month {month} outside [1, 12]")
    days_in_month = lookup[year][month - 1]
    if not 1 <= day <= days_in_month:
        raise ValueError(f"day {day} outside [1, {days_in_month}] for {year}-{month}")
    month_index = (year - _first_bs_year) * 12 + month - 1
    return date.fromordinal(_month_ordinals[month_index] + day - 1)


def ad_to_bs(ad: date) -> tuple[int, int, int]:
    """Return the BS (year, month, day) of the AD date `ad`.

    A datetime is accepted and its time of day ignored. Raise ValueError if
    `ad` is outside the supported range.
    """
    # date.toordinal(ad), not ad.toordinal(): it raises TypeError, not
    # AttributeError, if `ad` is not a date.
    ordinal = date.toordinal(ad)
    if not _month_ordinals[0] <= ordinal < _month_ordinals[-1]:
        raise ValueError(
            f"date {date.isoformat(ad)} outside "
            f"[{_min_ad.isoformat()}, {_max_ad.isoformat()}]"
        )
    # The last month that starts on or before `ad` is the one it falls in.
    month_index = bisect_right(_month_ordinals, ordinal) - 1
    years, month0 = divmod(month_index, 12)
    day = ordinal - _month_ordinals[month_index] + 1
    return _first_bs_year + years, month0 + 1, day


def _pad(value: int, width: int, mods: str, fill: str = "0") -> str:
    """Pad a number as GNU strftime does: "-" no padding, "_" spaces, "0" zeros."""
    if "-" in mods:
        return str(value)
    if "_" in mods:
        fill = " "
    elif "0" in mods:
        fill = "0"
    return f"{value:{fill}>{width}d}"


def _name(name: str, mods: str) -> str:
    """Format a month name; the GNU "^" flag makes it uppercase."""
    return name.upper() if "^" in mods else name


# A strftime directive: "%", optional GNU flags, then the conversion, which is
# one character or GNU's ":z" (time zone offset with a colon, like +05:45).
# For BS directives, "-", "_", "0" and "^" work as in GNU; "#" is ignored.
_DIRECTIVE = re.compile(r"%([-_0^#]*)(:z|[^-_0^#])")

# Directives that don't depend on the calendar (time of day, weekday, time
# zone, epoch) or that are documented as Gregorian (week numbers), and that
# both glibc and macOS support. They are formatted from the AD datetime; any
# other unknown directive is printed as is, as GNU date does.
_AD_DIRECTIVES = frozenset("aAuwHIklMSfpTRrXszZGgUVW")


def _format_directive(  # noqa: C901, PLR0911, PLR0912
    directive: re.Match[str], bs: "BSDate", dt: datetime
) -> str:
    mods, spec = directive.groups()
    year, month, day = bs.year, bs.month, bs.day
    match spec:
        case "Y":
            return _pad(year, 4, mods)
        case "y":
            return _pad(year % 100, 2, mods)
        case "C":
            return _pad(year // 100, 2, mods)
        case "m":
            return _pad(month, 2, mods)
        case "d":
            return _pad(day, 2, mods)
        case "e":
            return _pad(day, 2, mods, fill=" ")
        case "j":
            return _pad((bs.to_ad() - new_years[year]).days + 1, 3, mods)
        case "B":
            return _name(months[month - 1], mods)
        case "b" | "h":
            return _name(months[month - 1][:3], mods)
        case "F":
            return f"{year:04d}-{month:02d}-{day:02d}"
        case "D" | "x":  # %x as in the C locale
            return f"{month:02d}/{day:02d}/{year % 100:02d}"
        case "c":  # as in the C locale
            return _bs_strftime("%a %b %e %H:%M:%S %Y", bs, dt)
        case ":z":
            offset = dt.strftime("%z")  # "+0545", or "+054530" with seconds
            return ":".join([offset[:3], *re.findall(r"\d\d", offset[3:])])
        case "n":
            return "\n"
        case "t":
            return "\t"
        case "%":
            return "%"
        case _ if spec in _AD_DIRECTIVES:
            return dt.strftime(directive[0])
        case _:
            return directive[0]


def _bs_strftime(fmt: str, bs: "BSDate", dt: datetime) -> str:
    """Format `bs` with strftime directives; non-date ones are taken from `dt`."""
    return _DIRECTIVE.sub(lambda directive: _format_directive(directive, bs, dt), fmt)


# ASCII or Devanagari (U+0966..U+096F) digits; int() reads both.
_BS_DATE = re.compile(r"[0-9\u0966-\u096f]{4}(?:-[0-9\u0966-\u096f]{1,2}){2}")


def _parse_bs(bs_datestring: str) -> tuple[int, int, int]:
    if not _BS_DATE.fullmatch(bs_datestring):
        shown = bs_datestring[:40]
        suffix = "..." if len(bs_datestring) > len(shown) else ""
        raise ValueError(f"expected YYYY-M-D, got {shown!r}{suffix}")
    year, month, day = map(int, bs_datestring.split("-"))
    return year, month, day


@dataclass(frozen=True, order=True, slots=True)
class BSDate:
    """A Bikram Sambat date, with the interface of datetime.date.

    Supports timedelta arithmetic, subtraction of two BSDates, ordering,
    hashing, pickling, isoformat()/fromisoformat() and strftime().
    """

    min: ClassVar["BSDate"]
    max: ClassVar["BSDate"]
    resolution: ClassVar[timedelta] = timedelta(days=1)

    year: int
    month: int
    day: int
    _ad: date = field(init=False, compare=False, repr=False, hash=False)

    def __post_init__(self) -> None:
        # Store plain ints, as datetime.date does: not a bool or a Month member,
        # which would show in repr() and, on 3.10, in strftime("%-m").
        year, month, day = index(self.year), index(self.month), index(self.day)
        object.__setattr__(self, "year", year)
        object.__setattr__(self, "month", month)
        object.__setattr__(self, "day", day)
        # bs_to_ad validates; we cache the AD date for downstream operations.
        object.__setattr__(self, "_ad", bs_to_ad(year, month, day))

    @classmethod
    def today(cls) -> "BSDate":
        return cls.from_ad(date.today())

    @classmethod
    def fromtimestamp(cls, timestamp: float, /) -> "BSDate":
        return cls.from_ad(date.fromtimestamp(timestamp))

    @classmethod
    def fromisoformat(cls, date_string: str, /) -> "BSDate":
        """Parse "YYYY-M-D", with ASCII or Devanagari digits."""
        return cls(*_parse_bs(date_string))

    @classmethod
    def from_ad(cls, ad: date) -> "BSDate":
        return cls(*ad_to_bs(ad))

    def to_ad(self) -> date:
        return self._ad

    def replace(
        self, year: int | None = None, month: int | None = None, day: int | None = None
    ) -> "BSDate":
        return type(self)(
            year if year is not None else self.year,
            month if month is not None else self.month,
            day if day is not None else self.day,
        )

    # PEP 738: copy.replace() (Python 3.13+) dispatches to __replace__.
    __replace__ = replace

    def weekday(self) -> int:
        return self._ad.weekday()

    def isoweekday(self) -> int:
        return self._ad.isoweekday()

    def isoformat(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def strftime(self, fmt: str) -> str:
        """Format like date.strftime, with BS values for date directives.

        %Y %y %C %m %d %e %j %B %b %h %F %D %x %c use the BS date. Weekday,
        time and week-number directives (e.g. %a, %H, %U) are formatted from
        the equivalent AD date; any other directive is printed as is.
        """
        return _bs_strftime(fmt, self, datetime.combine(self._ad, time()))

    def __str__(self) -> str:
        return self.isoformat()

    def __add__(self, other: timedelta) -> "BSDate":
        if not isinstance(other, timedelta):
            return NotImplemented
        return type(self).from_ad(self._ad + other)

    __radd__ = __add__

    @overload
    def __sub__(self, other: timedelta) -> "BSDate": ...
    @overload
    def __sub__(self, other: "BSDate") -> timedelta: ...
    def __sub__(self, other: "timedelta | BSDate") -> "BSDate | timedelta":
        if isinstance(other, timedelta):
            return type(self).from_ad(self._ad - other)
        if isinstance(other, BSDate):
            return self._ad - other._ad
        return NotImplemented

    def __format__(self, fmt: str, /) -> str:
        return self.strftime(fmt) if fmt else str(self)


BSDate.min = BSDate(_first_bs_year, 1, 1)
BSDate.max = BSDate(_last_bs_year, 12, lookup[_last_bs_year][-1])
