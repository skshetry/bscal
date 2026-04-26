"""Tests for the stdlib-parallel APIs in bscal.cal."""

from bscal import BSDate
from bscal.cal import (
    BAISAKH,
    CHAITRA,
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
    expected = sum(isleap(y) for y in range(2080, 2090))
    assert leapdays(2080, 2090) == expected


def test_weekday() -> None:
    # AD 2024-04-13 == BS 2081-01-01 (Saturday); weekday Mon=0..Sun=6.
    assert weekday(2081, 1, 1) == 5  # noqa: PLR2004


def test_monthrange() -> None:
    # Baisakh 2081 starts on Saturday (weekday=5) and has 31 days.
    assert monthrange(2081, 1) == (5, 31)


def test_month_enum_values_match_indices() -> None:
    assert Month.BAISAKH.value == 1
    assert Month.CHAITRA.value == 12  # noqa: PLR2004
    assert BAISAKH is Month.BAISAKH
    assert CHAITRA is Month.CHAITRA


def test_month_enum_usable_in_apis() -> None:
    # IntEnum values pass through wherever an int month is accepted.
    assert monthrange(2081, BAISAKH) == monthrange(2081, 1)
    assert BSDate(2081, BAISAKH, 1) == BSDate(2081, 1, 1)
