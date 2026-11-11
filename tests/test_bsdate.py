import copy
import pickle
import sys
from datetime import date, datetime, timedelta

import pytest

from bscal import BSDate
from bscal.cal import BAISAKH

# AD 2024-04-13 == BS 2081-01-01 (Saturday)


def test_construct_and_attributes() -> None:
    bd = BSDate(2081, 1, 1)
    assert (bd.year, bd.month, bd.day) == (2081, 1, 1)


def test_fields_are_plain_ints() -> None:
    bd = BSDate(2081, BAISAKH, True)
    assert (type(bd.year), type(bd.month), type(bd.day)) == (int, int, int)
    assert repr(bd) == "BSDate(year=2081, month=1, day=1)"
    assert bd.strftime("%-m/%-d") == "1/1"


def test_construct_invalid_raises() -> None:
    with pytest.raises(ValueError, match=r"month 13 outside"):
        BSDate(2081, 13, 1)
    with pytest.raises(ValueError, match=r"day 100 outside"):
        BSDate(2081, 1, 100)
    with pytest.raises(ValueError, match=r"year 2200 outside \[1970, 2100\]"):
        BSDate(2200, 1, 1)


def test_to_ad() -> None:
    assert BSDate(2081, 1, 1).to_ad() == date(2024, 4, 13)


def test_from_ad() -> None:
    assert BSDate.from_ad(date(2024, 4, 13)) == BSDate(2081, 1, 1)


def test_today() -> None:
    bd = BSDate.today()
    assert bd.to_ad() == date.today()
    assert BSDate.from_ad(bd.to_ad()) == bd


def test_add_timedelta() -> None:
    assert BSDate(2081, 1, 1) + timedelta(days=1) == BSDate(2081, 1, 2)
    assert BSDate(2081, 1, 1) + timedelta(days=31) == BSDate(2081, 2, 1)


def test_radd_timedelta() -> None:
    assert timedelta(days=5) + BSDate(2081, 1, 1) == BSDate(2081, 1, 6)


def test_sub_timedelta() -> None:
    assert BSDate(2081, 1, 2) - timedelta(days=1) == BSDate(2081, 1, 1)


def test_arithmetic_with_unsupported_type_raises() -> None:
    with pytest.raises(TypeError):
        BSDate(2081, 1, 1) + 1  # type: ignore[operator]
    with pytest.raises(TypeError):
        BSDate(2081, 1, 1) - 1  # type: ignore[operator]


def test_arithmetic_past_supported_range_raises() -> None:
    with pytest.raises(ValueError, match="outside"):
        BSDate.max + timedelta(days=1)


def test_arithmetic_keeps_subclass() -> None:
    class MyDate(BSDate):
        pass

    d = MyDate(2081, 1, 1)
    assert type(d + timedelta(days=1)) is MyDate
    assert type(timedelta(days=1) + d) is MyDate
    assert type(d - timedelta(days=1)) is MyDate


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
    assert len(s) == 2


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
    assert BSDate(2081, 1, 1).weekday() == 5
    assert BSDate(2081, 1, 1).isoweekday() == 6


def test_isoformat_and_str() -> None:
    bd = BSDate(2081, 1, 1)
    assert bd.isoformat() == "2081-01-01"
    assert str(bd) == "2081-01-01"


@pytest.mark.parametrize(
    ("fmt", "expected"),
    [
        ("%Y-%m-%d", "2081-01-01"),
        ("%y %C", "81 20"),
        ("%-m/%-d %_m %e", "1/1  1  1"),
        ("%j", "001"),
        ("%B %b %h", "Baisakh Bai Bai"),
        ("%F | %D", "2081-01-01 | 01/01/81"),
        # %x and %c follow the C locale ("%m/%d/%y", "%a %b %e %H:%M:%S %Y").
        ("%x", "01/01/81"),
        ("%c", "Sat Bai  1 00:00:00 2081"),
        ("%n%t%%", "\n\t%"),
        ("%a %A %H:%M", "Sat Saturday 00:00"),  # delegated to datetime.strftime
        ("%:z", ""),  # naive datetime: no offset
        ("100%", "100%"),  # trailing lone '%' is kept verbatim
    ],
)
def test_strftime(fmt: str, expected: str) -> None:
    assert BSDate(2081, 1, 1).strftime(fmt) == expected


def test_strftime_day_of_year_in_leap_year() -> None:
    assert BSDate(2081, 12, 31).strftime("%j") == "366"


@pytest.mark.parametrize("directive", ["%Q", "%+", "%Ey", "%-Q", "%\x00"])
def test_strftime_unknown_directive_printed_as_is(directive: str) -> None:
    assert BSDate(2081, 1, 1).strftime(f"<{directive}>") == f"<{directive}>"


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_round_trip_preserves_cache(protocol: int) -> None:
    bd = BSDate(2081, 1, 1)
    bd2 = pickle.loads(pickle.dumps(bd, protocol=protocol))
    assert bd2 == bd
    assert hash(bd2) == hash(bd)
    assert bd2.to_ad() == date(2024, 4, 13)


def test_deepcopy() -> None:
    bd = BSDate(2081, 1, 1)
    assert copy.deepcopy(bd) == bd


def test_class_min_max_resolution() -> None:
    assert BSDate.min == BSDate(1970, 1, 1)
    assert BSDate.max == BSDate(2100, 12, 30)
    assert BSDate.resolution == timedelta(days=1)


def test_fromtimestamp() -> None:
    noon = datetime(2024, 4, 13, 12).timestamp()  # local noon, same date in any TZ
    assert BSDate.fromtimestamp(noon) == BSDate(2081, 1, 1)


def test_fromisoformat() -> None:
    assert BSDate.fromisoformat("2081-01-01") == BSDate(2081, 1, 1)
    # Tolerant of unpadded month/day, matching _parse_bs.
    assert BSDate.fromisoformat("2081-1-1") == BSDate(2081, 1, 1)


def test_fromisoformat_devanagari_digits() -> None:
    assert BSDate.fromisoformat("२०८१-१-१") == BSDate(2081, 1, 1)
    assert BSDate.fromisoformat("२०८१-०५-१५") == BSDate(2081, 5, 15)


def test_fromisoformat_round_trips_isoformat() -> None:
    bd = BSDate(2081, 5, 15)
    assert BSDate.fromisoformat(bd.isoformat()) == bd


@pytest.mark.parametrize(
    "date_string",
    [
        "2081/01/01",
        " 2081-1-1",
        "2081-1-1\n",
        "2081 - 1 - 1",
        "2_081-0_1-01",
        "+2081-+1-+1",
        "\uff12\uff10\uff18\uff11-1-1",  # fullwidth digits
        "81-1-1",
        "2081-001-01",
        "2081-1",
    ],
)
def test_fromisoformat_invalid_raises(date_string: str) -> None:
    with pytest.raises(ValueError, match="expected YYYY-M-D"):
        BSDate.fromisoformat(date_string)


def test_fromisoformat_error_truncates_long_input() -> None:
    with pytest.raises(ValueError, match=r"got '1{40}'\.\.\.$"):
        BSDate.fromisoformat("1" * 10_000)


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
    bd = BSDate(2081, 1, 1)
    # `if sys.version_info` narrows attr availability for static checkers;
    # the @skipif above guards runtime execution on pre-3.13.
    if sys.version_info >= (3, 13):
        assert copy.replace(bd, year=2080) == BSDate(2080, 1, 1)
