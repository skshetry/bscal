import calendar
import contextlib
from collections.abc import Iterator, Sequence
from datetime import date, datetime, timedelta
from itertools import repeat
from typing import Optional

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
    2083: [31, 31, 32, 31, 31, 30, 30, 30, 29, 30, 30, 30],
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
new_years = {
    # bs_year: ad_date_for_bs_new_year
    1970: date(1913, 4, 13),
    1971: date(1914, 4, 13),
    1972: date(1915, 4, 13),
    1973: date(1916, 4, 13),
    1974: date(1917, 4, 13),
    1975: date(1918, 4, 13),
    1976: date(1919, 4, 13),
    1977: date(1920, 4, 13),
    1978: date(1921, 4, 13),
    1979: date(1922, 4, 13),
    1980: date(1923, 4, 13),
    1981: date(1924, 4, 13),
    1982: date(1925, 4, 13),
    1983: date(1926, 4, 13),
    1984: date(1927, 4, 13),
    1985: date(1928, 4, 13),
    1986: date(1929, 4, 13),
    1987: date(1930, 4, 13),
    1988: date(1931, 4, 13),
    1989: date(1932, 4, 13),
    1990: date(1933, 4, 13),
    1991: date(1934, 4, 13),
    1992: date(1935, 4, 13),
    1993: date(1936, 4, 13),
    1994: date(1937, 4, 13),
    1995: date(1938, 4, 13),
    1996: date(1939, 4, 13),
    1997: date(1940, 4, 13),
    1998: date(1941, 4, 13),
    1999: date(1942, 4, 13),
    2000: date(1943, 4, 14),
    2001: date(1944, 4, 13),
    2002: date(1945, 4, 13),
    2003: date(1946, 4, 13),
    2004: date(1947, 4, 14),
    2005: date(1948, 4, 13),
    2006: date(1949, 4, 13),
    2007: date(1950, 4, 13),
    2008: date(1951, 4, 14),
    2009: date(1952, 4, 13),
    2010: date(1953, 4, 13),
    2011: date(1954, 4, 13),
    2012: date(1955, 4, 14),
    2013: date(1956, 4, 13),
    2014: date(1957, 4, 13),
    2015: date(1958, 4, 13),
    2016: date(1959, 4, 14),
    2017: date(1960, 4, 13),
    2018: date(1961, 4, 13),
    2019: date(1962, 4, 13),
    2020: date(1963, 4, 14),
    2021: date(1964, 4, 13),
    2022: date(1965, 4, 13),
    2023: date(1966, 4, 13),
    2024: date(1967, 4, 14),
    2025: date(1968, 4, 13),
    2026: date(1969, 4, 13),
    2027: date(1970, 4, 14),
    2028: date(1971, 4, 14),
    2029: date(1972, 4, 13),
    2030: date(1973, 4, 13),
    2031: date(1974, 4, 14),
    2032: date(1975, 4, 14),
    2033: date(1976, 4, 13),
    2034: date(1977, 4, 13),
    2035: date(1978, 4, 14),
    2036: date(1979, 4, 14),
    2037: date(1980, 4, 13),
    2038: date(1981, 4, 13),
    2039: date(1982, 4, 14),
    2040: date(1983, 4, 14),
    2041: date(1984, 4, 13),
    2042: date(1985, 4, 13),
    2043: date(1986, 4, 14),
    2044: date(1987, 4, 14),
    2045: date(1988, 4, 13),
    2046: date(1989, 4, 13),
    2047: date(1990, 4, 14),
    2048: date(1991, 4, 14),
    2049: date(1992, 4, 13),
    2050: date(1993, 4, 13),
    2051: date(1994, 4, 14),
    2052: date(1995, 4, 14),
    2053: date(1996, 4, 13),
    2054: date(1997, 4, 13),
    2055: date(1998, 4, 14),
    2056: date(1999, 4, 14),
    2057: date(2000, 4, 13),
    2058: date(2001, 4, 14),
    2059: date(2002, 4, 14),
    2060: date(2003, 4, 14),
    2061: date(2004, 4, 13),
    2062: date(2005, 4, 14),
    2063: date(2006, 4, 14),
    2064: date(2007, 4, 14),
    2065: date(2008, 4, 13),
    2066: date(2009, 4, 14),
    2067: date(2010, 4, 14),
    2068: date(2011, 4, 14),
    2069: date(2012, 4, 13),
    2070: date(2013, 4, 14),
    2071: date(2014, 4, 14),
    2072: date(2015, 4, 14),
    2073: date(2016, 4, 13),
    2074: date(2017, 4, 14),
    2075: date(2018, 4, 14),
    2076: date(2019, 4, 14),
    2077: date(2020, 4, 13),
    2078: date(2021, 4, 14),
    2079: date(2022, 4, 14),
    2080: date(2023, 4, 14),
    2081: date(2024, 4, 13),
    2082: date(2025, 4, 14),
    2083: date(2026, 4, 14),
    2084: date(2027, 4, 14),
    2085: date(2028, 4, 13),
    2086: date(2029, 4, 14),
    2087: date(2030, 4, 14),
    2088: date(2031, 4, 15),
    2089: date(2032, 4, 14),
    2090: date(2033, 4, 14),
    2091: date(2034, 4, 14),
    2092: date(2035, 4, 14),
    2093: date(2036, 4, 14),
    2094: date(2037, 4, 14),
    2095: date(2038, 4, 14),
    2096: date(2039, 4, 14),
    2097: date(2040, 4, 14),
    2098: date(2041, 4, 14),
    2099: date(2042, 4, 14),
    2100: date(2043, 4, 14),
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


def bs_to_ad(year: int, month: int, day: int) -> date:
    months_data = lookup[year]
    days = sum(months_data[: month - 1]) + day - 1
    return new_years[year] + timedelta(days)


def ad_to_bs(ad: date, start: Optional[int] = None) -> tuple[int, int, int]:
    start = start or next(iter(lookup))
    difference = ad - new_years[start]
    for year, months_data in lookup.items():
        if year < start:
            continue
        days_in_year = sum(months_data)
        if difference.days < days_in_year:
            break
        difference -= timedelta(days_in_year)
    else:
        raise AssertionError("outside of range")  # noqa: TRY003

    month = 1
    for month, days in enumerate(months_data, start=1):  # noqa: B007
        if difference.days < days:
            break
        difference -= timedelta(days)
    return year, month, difference.days + 1


class BSCalendar(calendar.TextCalendar):
    def __init__(
        self, firstweekday: int = 0, to_highlight: tuple[int, ...] = ()
    ) -> None:
        super().__init__(firstweekday)
        self._to_highlight = to_highlight
        self._formatting_ctx: tuple[int, ...] = ()

    def formatmonthname(
        self, theyear: int, themonth: int, width: int, withyear: bool = True
    ) -> str:
        """Return a formatted month name."""
        s = months[themonth - 1]
        if withyear:
            s = f"{s} {theyear!r}"
        return s.center(width)

    def itermonthdays(self, year: int, month: int) -> Iterator[int]:
        """Like itermonthdates(), but will yield day numbers. For days outside
        the specified month the day number is 0.
        """
        ndays = lookup[year][month - 1]
        day1_dt = bs_to_ad(year, month, 1)
        day1 = day1_dt.weekday()
        days_before = (day1 - self.firstweekday) % 7
        yield from repeat(0, days_before)
        yield from range(1, ndays + 1)
        days_after = (self.firstweekday - day1 - ndays) % 7
        yield from repeat(0, days_after)

    def formatmonth(self, theyear: int, themonth: int, w: int = 0, l: int = 0) -> str:  # noqa: E741
        self._formatting_ctx = (theyear, themonth)
        return super().formatmonth(theyear, themonth, w, l)

    def formatday(self, day: int, weekday: int, width: int) -> str:
        s = super().formatday(day, weekday, width)
        if (*self._formatting_ctx, day) == self._to_highlight:
            s = f"\033[30;47m{s}\033[0m"
        return s


def bsconv(bs_datestring: str) -> None:
    year, month, day, *_ = map(int, bs_datestring.split("-"))
    ad = bs_to_ad(year, month, day)
    ad_tz = datetime.combine(ad, datetime.now().time()).astimezone()
    print(ad_tz.strftime("%a %b %e %T %Z %Y"))


def bsdate(args: Optional[Sequence[str]] = None) -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        required=False,
        metavar="<bs_date>",
        help="Convert BS date to AD format",
        dest="convert",
    )
    parser.add_argument(
        "date",
        nargs="?",
        metavar="STRING",
        help="Convert given datetime string (isoformat/unix-timestamp) to BS format",
    )
    opt = parser.parse_args(args)
    if opt.convert:
        bsconv(opt.convert)
        return

    dt: Optional[datetime] = None
    if opt.date:
        with contextlib.suppress(ValueError):
            dt = datetime.fromtimestamp(int(opt.date.lstrip("@")))
    if not dt and opt.date:
        try:
            _date = date.fromisoformat(opt.date)
        except ValueError:
            dt = datetime.fromisoformat(opt.date)
        else:
            dt = datetime.combine(_date, datetime.now().time())

    dt = dt or datetime.now()
    dt = dt.astimezone()
    year, month, day = ad_to_bs(dt.date())
    print(dt.strftime("%a"), months[month - 1], day, dt.strftime("%T %Z"), year)


def cal(args: Optional[Sequence[str]] = None) -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("year", nargs="?", type=int, help="year number (1-9999)")
    parser.add_argument(
        "month",
        nargs="?",
        type=int,
        help="month number (1-12, text only)",
    )
    opt = parser.parse_args(args)

    year, month, day = ad_to_bs(date.today())
    cal = BSCalendar(6, to_highlight=(year, month, day) if sys.stdout.isatty() else ())
    if not opt.year or opt.month:
        result = cal.formatmonth(opt.year or year, opt.month or month)
    else:
        result = cal.formatyear(opt.year)
    print(result)


if __name__ == "__main__":
    cal()
