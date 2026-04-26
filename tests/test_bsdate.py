import copy
import pickle
import sys
from datetime import date, timedelta

import pytest

from bscal import BSDate

# AD 2024-04-13 == BS 2081-01-01 (Saturday)


def test_construct_and_attributes() -> None:
    bd = BSDate(2081, 1, 1)
    assert (bd.year, bd.month, bd.day) == (2081, 1, 1)


def test_construct_invalid_raises() -> None:
    with pytest.raises(ValueError, match=r"month 13 outside"):
        BSDate(2081, 13, 1)
    with pytest.raises(ValueError, match=r"day 100 outside"):
        BSDate(2081, 1, 100)
    with pytest.raises(ValueError, match="outside of range"):
        BSDate(2200, 1, 1)


def test_to_ad() -> None:
    assert BSDate(2081, 1, 1).to_ad() == date(2024, 4, 13)


def test_from_ad() -> None:
    assert BSDate.from_ad(date(2024, 4, 13)) == BSDate(2081, 1, 1)


def test_today_round_trips() -> None:
    bd = BSDate.today()
    assert BSDate.from_ad(bd.to_ad()) == bd


def test_add_timedelta() -> None:
    assert BSDate(2081, 1, 1) + timedelta(days=1) == BSDate(2081, 1, 2)
    assert BSDate(2081, 1, 1) + timedelta(days=31) == BSDate(2081, 2, 1)


def test_radd_timedelta() -> None:
    assert timedelta(days=5) + BSDate(2081, 1, 1) == BSDate(2081, 1, 6)


def test_sub_timedelta() -> None:
    assert BSDate(2081, 1, 2) - timedelta(days=1) == BSDate(2081, 1, 1)


def test_sub_bsdate_returns_timedelta() -> None:
    diff = BSDate(2081, 2, 1) - BSDate(2081, 1, 1)
    assert diff == timedelta(days=31)


def test_ordering_chronological() -> None:
    assert BSDate(2080, 12, 30) < BSDate(2081, 1, 1)
    assert BSDate(2081, 1, 1) < BSDate(2081, 1, 2)
    assert BSDate(2081, 1, 1) <= BSDate(2081, 1, 1)
    assert sorted([BSDate(2081, 5, 1), BSDate(2080, 1, 1)]) == [
        BSDate(2080, 1, 1),
        BSDate(2081, 5, 1),
    ]


def test_hashable() -> None:
    s = {BSDate(2081, 1, 1), BSDate(2081, 1, 1), BSDate(2081, 1, 2)}
    assert len(s) == 2  # noqa: PLR2004


def test_immutable() -> None:
    bd = BSDate(2081, 1, 1)
    with pytest.raises(AttributeError):
        # frozen=True raises FrozenInstanceError (an AttributeError subclass).
        bd.year = 2080  # type: ignore[misc]  # ty: ignore[invalid-assignment]


def test_replace() -> None:
    bd = BSDate(2081, 1, 1)
    assert bd.replace(year=2080) == BSDate(2080, 1, 1)
    assert bd.replace(month=5) == BSDate(2081, 5, 1)
    assert bd.replace(day=15) == BSDate(2081, 1, 15)
    assert bd.replace(year=2080, month=5, day=15) == BSDate(2080, 5, 15)


def test_weekday() -> None:
    # AD 2024-04-13 is Saturday; weekday() returns 5 (Mon=0).
    assert BSDate(2081, 1, 1).weekday() == 5  # noqa: PLR2004
    assert BSDate(2081, 1, 1).isoweekday() == 6  # noqa: PLR2004


def test_isoformat_and_str() -> None:
    bd = BSDate(2081, 1, 1)
    assert bd.isoformat() == "2081-01-01"
    assert str(bd) == "2081-01-01"


def test_strftime_bs_aware() -> None:
    assert BSDate(2081, 1, 1).strftime("%Y-%m-%d %B") == "2081-01-01 Baisakh"


def test_strftime_with_weekday_uses_ad() -> None:
    # %a/%A are calendar-independent; they reflect the underlying weekday.
    assert BSDate(2081, 1, 1).strftime("%a") == "Sat"


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_round_trip_preserves_cache(protocol: int) -> None:
    bd = BSDate(2081, 1, 1)
    bd2 = pickle.loads(pickle.dumps(bd, protocol=protocol))  # noqa: S301
    assert bd2 == bd
    assert hash(bd2) == hash(bd)
    assert bd2._ad == date(2024, 4, 13)  # noqa: SLF001


def test_deepcopy() -> None:
    bd = BSDate(2081, 1, 1)
    assert copy.deepcopy(bd) == bd


def test_class_min_max_resolution() -> None:
    assert BSDate.min == BSDate(1970, 1, 1)
    assert BSDate.max == BSDate(2100, 12, 30)
    assert BSDate.resolution == timedelta(days=1)


def test_fromtimestamp_epoch() -> None:
    # Unix epoch (AD 1970-01-01) → BS 2026-09-17
    assert BSDate.fromtimestamp(0) == BSDate(2026, 9, 17)


def test_fromisoformat() -> None:
    assert BSDate.fromisoformat("2081-01-01") == BSDate(2081, 1, 1)
    # Tolerant of unpadded month/day, matching _parse_bs.
    assert BSDate.fromisoformat("2081-1-1") == BSDate(2081, 1, 1)


def test_fromisoformat_round_trips_isoformat() -> None:
    bd = BSDate(2081, 5, 15)
    assert BSDate.fromisoformat(bd.isoformat()) == bd


def test_fromisoformat_invalid_raises() -> None:
    with pytest.raises(ValueError, match="expected YYYY-M-D"):
        BSDate.fromisoformat("2081/01/01")


def test_format_with_strftime_spec() -> None:
    bd = BSDate(2081, 1, 1)
    assert f"{bd:%Y-%m-%d}" == "2081-01-01"
    assert f"{bd:%B %-d}" == "Baisakh 1"


def test_format_empty_spec_returns_str() -> None:
    bd = BSDate(2081, 1, 1)
    assert f"{bd}" == "2081-01-01"
    assert format(bd, "") == "2081-01-01"


@pytest.mark.skipif(
    sys.version_info < (3, 13), reason="copy.replace() needs Python 3.13+"
)
def test_copy_replace() -> None:
    import copy

    bd = BSDate(2081, 1, 1)
    # `if sys.version_info` narrows attr availability for static checkers;
    # the @skipif above guards runtime execution on pre-3.13.
    if sys.version_info >= (3, 13):
        assert copy.replace(bd, year=2080) == BSDate(2080, 1, 1)
