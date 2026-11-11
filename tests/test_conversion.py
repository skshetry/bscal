from datetime import date, datetime, timedelta

import pytest

from bscal import BSDate, ad_to_bs, bs_to_ad, lookup, new_years

# Published AD dates of BS new year (1 Baisakh). Independent of `lookup`, so a
# wrong month length anywhere shifts every later new year and fails the test.
EXPECTED_NEW_YEARS = {
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


def test_every_supported_day() -> None:
    # Walk every BS day in order next to an AD day counter. This checks both
    # directions against plain counting, not just against each other.
    ad = date(1913, 4, 13)
    for year, month_lengths in lookup.items():
        for month, ndays in enumerate(month_lengths, start=1):
            for day in range(1, ndays + 1):
                assert ad_to_bs(ad) == (year, month, day), ad
                assert bs_to_ad(year, month, day) == ad
                ad += timedelta(days=1)
    assert ad == date(2044, 4, 13)  # one past the last supported day


def test_new_years_match_published_dates() -> None:
    assert list(new_years) == list(range(1970, 2101))
    assert new_years == EXPECTED_NEW_YEARS


@pytest.mark.parametrize(
    "args", [(2080, 1, 1.5), (2080.0, 1, 1), ("2080", 1, 1), (2080, 1.5, 1)]
)
def test_bs_to_ad_rejects_non_integers(args: tuple[object, object, object]) -> None:
    with pytest.raises(TypeError):
        bs_to_ad(*args)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        BSDate(*args)  # type: ignore[arg-type]


def test_ad_to_bs_accepts_datetime() -> None:
    assert ad_to_bs(datetime(2024, 1, 1, 23, 59)) == ad_to_bs(date(2024, 1, 1))


@pytest.mark.parametrize("value", ["2024-01-01", None, 5])
def test_ad_to_bs_rejects_non_dates(value: object) -> None:
    with pytest.raises(TypeError):
        ad_to_bs(value)  # type: ignore[arg-type]


def test_ad_to_bs_after_range_raises() -> None:
    # BS 2100-12-30 == AD 2044-04-12 is the last supported day.
    with pytest.raises(ValueError, match=r"date 2044-04-13 outside"):
        ad_to_bs(date(2044, 4, 13))


def test_ad_to_bs_before_range_raises() -> None:
    # BS 1970-01-01 == AD 1913-04-13 is the first supported day.
    with pytest.raises(ValueError, match=r"date 1913-04-12 outside"):
        ad_to_bs(min(new_years.values()) - timedelta(days=1))


def test_bs_to_ad_unknown_year_raises() -> None:
    with pytest.raises(ValueError, match=r"year 2200 outside \[1970, 2100\]"):
        bs_to_ad(2200, 1, 1)


def test_bs_to_ad_invalid_month_raises() -> None:
    with pytest.raises(ValueError, match=r"month 13 outside"):
        bs_to_ad(2080, 13, 1)
    with pytest.raises(ValueError, match=r"month 0 outside"):
        bs_to_ad(2080, 0, 1)


def test_bs_to_ad_invalid_day_raises() -> None:
    with pytest.raises(ValueError, match=r"day 100 outside"):
        bs_to_ad(2080, 1, 100)
    with pytest.raises(ValueError, match=r"day 0 outside"):
        bs_to_ad(2080, 1, 0)


def test_lookup_well_formed() -> None:
    for year, month_lengths in lookup.items():
        assert len(month_lengths) == 12, f"year {year}: {len(month_lengths)} months"
        days = sum(month_lengths)
        assert 365 <= days <= 366, f"year {year} has {days} days"
        assert all(28 <= m <= 32 for m in month_lengths), f"{year}: {month_lengths}"
