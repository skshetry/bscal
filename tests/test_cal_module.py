"""Tests for the stdlib-parallel APIs in bscal.cal."""

from itertools import pairwise

import pytest

from bscal import BSDate, lookup
from bscal.cal import (
    BAISAKH,
    CHAITRA,
    BSCalendar,
    Month,
    isleap,
    leapdays,
    month_abbr,
    month_name,
    monthrange,
    weekday,
)


def test_month_name_one_indexed() -> None:
    assert month_name[0] == ""  # sentinel
    assert month_name[1] == "Baisakh"
    assert month_name[12] == "Chaitra"
    assert month_abbr[0] == ""
    assert month_abbr[1] == "Bai"


def test_isleap() -> None:
    # BS 2081 has 366 days; BS 2080 has 365.
    assert isleap(2081) is True
    assert isleap(2080) is False


def test_leapdays() -> None:
    # 366-day years in [2080, 2090): 2081, 2085, 2087 (see lookup).
    assert leapdays(2080, 2090) == 3
    assert leapdays(2080, 2080) == 0


def test_weekday() -> None:
    # AD 2024-04-13 == BS 2081-01-01 (Saturday); weekday Mon=0..Sun=6.
    assert weekday(2081, 1, 1) == 5


def test_monthrange() -> None:
    # Baisakh 2081 starts on Saturday (weekday=5) and has 31 days.
    assert monthrange(2081, 1) == (5, 31)


def test_month_enum_values_match_indices() -> None:
    assert Month.BAISAKH.value == 1
    assert Month.CHAITRA.value == 12
    assert BAISAKH is Month.BAISAKH
    assert CHAITRA is Month.CHAITRA


def test_month_enum_usable_in_apis() -> None:
    # IntEnum values pass through wherever an int month is accepted.
    assert monthrange(2081, BAISAKH) == monthrange(2081, 1)
    assert BSDate(2081, BAISAKH, 1) == BSDate(2081, 1, 1)


@pytest.mark.parametrize("year", [2080.0, "2080", None])
def test_isleap_rejects_non_integers(year: object) -> None:
    with pytest.raises(TypeError):
        isleap(year)  # type: ignore[arg-type]


def test_isleap_outside_range_raises() -> None:
    with pytest.raises(ValueError, match=r"year 1900 outside \[1970, 2100\]"):
        isleap(1900)
    with pytest.raises(ValueError, match=r"year 1960 outside \[1970, 2100\]"):
        leapdays(1960, 1980)


@pytest.mark.parametrize("firstweekday", range(7))
@pytest.mark.parametrize(("year", "month"), [(2083, 1), (2083, 7), (2083, 12)])
def test_itermonthdays3_follows_bs_calendar(
    firstweekday: int, year: int, month: int
) -> None:
    days = list(BSCalendar(firstweekday).itermonthdays3(year, month))
    assert len(days) % 7 == 0
    # Consecutive BS days, starting on firstweekday, covering the whole month.
    dates = [BSDate(*d) for d in days]
    assert dates[0].weekday() == firstweekday
    assert all(b - a == BSDate.resolution for a, b in pairwise(dates))
    assert [d for d in days if d[:2] == (year, month)] == [
        (year, month, d) for d in range(1, lookup[year][month - 1] + 1)
    ]


def test_itermonthdays4_weekdays_match_bs_dates() -> None:
    for y, m, d, wd in BSCalendar(6).itermonthdays4(2083, 7):
        assert BSDate(y, m, d).weekday() == wd


def test_monthdatescalendar_yields_bsdates() -> None:
    weeks = BSCalendar(6).monthdatescalendar(2083, 7)
    days = [d for week in weeks for d in week]
    assert all(isinstance(d, BSDate) for d in days)
    assert BSDate(2083, 7, 1) in days
    assert BSDate(2083, 7, 30) in days


def test_itermonthdays3_padding_outside_range_raises() -> None:
    # Baisakh 1970 starts on Sunday, so a Monday-first week needs Chaitra 1969.
    with pytest.raises(ValueError, match=r"year 1969 outside \[1970, 2100\]"):
        list(BSCalendar(0).itermonthdays3(1970, 1))
    # Chaitra 2100 ends on Tuesday, so a Monday-first week needs Baisakh 2101.
    with pytest.raises(ValueError, match=r"year 2101 outside \[1970, 2100\]"):
        list(BSCalendar(0).itermonthdays3(2100, 12))
    # A Sunday-first week needs no padding before Baisakh 1970.
    assert next(BSCalendar(6).itermonthdays3(1970, 1)) == (1970, 1, 1)
