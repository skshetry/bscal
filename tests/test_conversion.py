from datetime import date, timedelta

import pytest
from hypothesis import given
from hypothesis.strategies import dates

from bscal import ad_to_bs, bs_to_ad, lookup, new_years


@given(dates(min(new_years.values()), max(new_years.values())))
def test(date: date) -> None:
    bs_year, bs_month, bs_day = ad_to_bs(date)
    assert bs_to_ad(bs_year, bs_month, bs_day) == date


def test_ad_to_bs_after_range_raises() -> None:
    # BS 2100-12-30 == AD 2044-04-12 is the last supported day.
    with pytest.raises(ValueError, match=r"date 2044-04-13 outside"):
        ad_to_bs(date(2044, 4, 13))


def test_ad_to_bs_before_range_raises() -> None:
    # BS 1970-01-01 == AD 1913-04-13 is the first supported day.
    with pytest.raises(ValueError, match=r"date 1913-04-12 outside"):
        ad_to_bs(min(new_years.values()) - timedelta(days=1))


def test_bs_to_ad_unknown_year_raises() -> None:
    with pytest.raises(ValueError, match="outside of range"):
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
    for year, months in lookup.items():
        assert len(months) == 12, f"year {year} has {len(months)} months"  # noqa: PLR2004
        assert 365 <= sum(months) <= 366, f"year {year} has {sum(months)} days"  # noqa: PLR2004
        assert all(28 <= m <= 32 for m in months), f"year {year} months: {months}"  # noqa: PLR2004
