import re
import time

import pytest

from bscal.bsdate import bsconv
from bscal.bsdate import main as bsdate
from bscal.cal import _CLICalendar
from bscal.cal import main as cal

HIGHLIGHT = "\033[30;43m"
RESET = "\033[0m"

results_2080_poush = """\
     Poush 2080
Su Mo Tu We Th Fr Sa
 1  2  3  4  5  6  7
 8  9 10 11 12 13 14
15 16 17 18 19 20 21
22 23 24 25 26 27 28
29

"""

results_2080 = """\
                                  2080

      Baisakh                    Jestha                    Asadh
Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa
                1  2          1  2  3  4  5  6                      1  2
 3  4  5  6  7  8  9       7  8  9 10 11 12 13       3  4  5  6  7  8  9
10 11 12 13 14 15 16      14 15 16 17 18 19 20      10 11 12 13 14 15 16
17 18 19 20 21 22 23      21 22 23 24 25 26 27      17 18 19 20 21 22 23
24 25 26 27 28 29 30      28 29 30 31 32            24 25 26 27 28 29 30
31                                                  31

      Shrawan                    Bhadra                     Asoj
Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa
    1  2  3  4  5  6                      1  2          1  2  3  4  5  6
 7  8  9 10 11 12 13       3  4  5  6  7  8  9       7  8  9 10 11 12 13
14 15 16 17 18 19 20      10 11 12 13 14 15 16      14 15 16 17 18 19 20
21 22 23 24 25 26 27      17 18 19 20 21 22 23      21 22 23 24 25 26 27
28 29 30 31 32            24 25 26 27 28 29 30      28 29 30
                          31

       Kartik                   Mangsir                    Poush
Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa
          1  2  3  4                      1  2       1  2  3  4  5  6  7
 5  6  7  8  9 10 11       3  4  5  6  7  8  9       8  9 10 11 12 13 14
12 13 14 15 16 17 18      10 11 12 13 14 15 16      15 16 17 18 19 20 21
19 20 21 22 23 24 25      17 18 19 20 21 22 23      22 23 24 25 26 27 28
26 27 28 29 30            24 25 26 27 28 29 30      29

        Magh                     Falgun                   Chaitra
Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa      Su Mo Tu We Th Fr Sa
    1  2  3  4  5  6             1  2  3  4  5                   1  2  3
 7  8  9 10 11 12 13       6  7  8  9 10 11 12       4  5  6  7  8  9 10
14 15 16 17 18 19 20      13 14 15 16 17 18 19      11 12 13 14 15 16 17
21 22 23 24 25 26 27      20 21 22 23 24 25 26      18 19 20 21 22 23 24
28 29                     27 28 29 30               25 26 27 28 29 30

"""


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("2080", "9"), results_2080_poush),
        (("2080",), results_2080),
    ],
)
def test_bscal_output(
    capsys: pytest.CaptureFixture[str],
    args: tuple[str, ...],
    expected: str,
) -> None:
    cal(args)
    out, err = capsys.readouterr()
    assert out == expected
    assert not err


def test_month_view_highlights_target_day_only() -> None:
    out = _CLICalendar(highlight_day=(2080, 9, 5), firstweekday=6).formatmonth(2080, 9)
    assert f"{HIGHLIGHT} 5{RESET}" in out
    assert out.count(HIGHLIGHT) == 1


def test_year_view_highlights_only_in_target_month() -> None:
    # Day 5 also exists in every other month — verify only Poush 5 is highlighted.
    out = _CLICalendar(highlight_day=(2080, 9, 5), firstweekday=6).formatyear(2080)
    assert out.count(HIGHLIGHT) == 1
    assert f"{HIGHLIGHT} 5{RESET}" in out


def test_no_highlight_when_unset() -> None:
    out = _CLICalendar(highlight_day=None, firstweekday=6).formatmonth(2080, 9)
    assert HIGHLIGHT not in out


# AD 2024-04-13 == BS 2081-01-01 (Baisakh 1, a Saturday)


def test_bsdate_ad_date_to_bs(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["2024-04-13"])
    # Default output: "<weekday> <month> <day> <HH:MM:SS> <tz> <year>"
    parts = capsys.readouterr().out.split()
    assert (parts[:3], parts[-1]) == (["Sat", "Baisakh", "1"], "2081")


def test_bsdate_ad_datetime_to_bs(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["2024-04-13T12:00:00"])
    parts = capsys.readouterr().out.split()
    assert (parts[:4], parts[-1]) == (["Sat", "Baisakh", "1", "12:00:00"], "2081")


def test_bsdate_convert_bs_to_ad(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-c", "2081-01-01"])
    parts = capsys.readouterr().out.split()
    assert (parts[:3], parts[-1]) == (["Sat", "Apr", "13"], "2024")


def test_bsconv(capsys: pytest.CaptureFixture[str]) -> None:
    bsconv("2081-01-01")
    parts = capsys.readouterr().out.split()
    assert (parts[:3], parts[-1]) == (["Sat", "Apr", "13"], "2024")


# GNU/BSD date(1) compatibility


def test_bsdate_iso_8601_short(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-I", "2024-04-13T12:34:56"])
    assert capsys.readouterr().out == "2081-01-01\n"


def test_bsdate_iso_8601_attached_seconds(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-Iseconds", "2024-04-13T12:34:56+05:45"])
    assert capsys.readouterr().out == "2081-01-01T12:34:56+05:45\n"


def test_bsdate_iso_8601_long_form(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["--iso-8601=hours", "2024-04-13T12:34:56+05:45"])
    assert capsys.readouterr().out == "2081-01-01T12+05:45\n"


def test_bsdate_plus_format_bs_aware(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["+%Y-%m-%d %B %A", "2024-04-13T12:00:00"])
    assert capsys.readouterr().out == "2081-01-01 Baisakh Saturday\n"


def test_bsdate_plus_format_modifiers(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["+%-d %_d %0d %j %F", "2024-04-13"])
    assert capsys.readouterr().out == "1  1 01 001 2081-01-01\n"


def test_bsdate_convert_iso(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-c", "2081-01-01", "-I"])
    assert capsys.readouterr().out == "2024-04-13\n"


def test_bsdate_convert_plus_format(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-c", "2081-01-01", "+%F"])
    assert capsys.readouterr().out == "2024-04-13\n"


def test_bsdate_utc_iso(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-u", "-Iseconds", "2024-04-13T12:34:56+05:45"])
    assert capsys.readouterr().out == "2081-01-01T06:49:56+00:00\n"


def test_bsdate_invalid_iso_fmt(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        bsdate(["-Inanos", "2024-04-13"])
    assert exc_info.value.code == 2
    assert "invalid ISO format 'nanos'" in capsys.readouterr().err


def test_bsdate_format_modes_mutually_exclusive(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        bsdate(["+%F", "-I", "2024-04-13"])
    assert exc_info.value.code == 2
    assert "mutually exclusive" in capsys.readouterr().err


def test_bsdate_convert_iso_seconds(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-u", "-c", "2081-01-01", "-Iseconds"])
    out = capsys.readouterr().out
    assert re.fullmatch(r"2024-04-13T\d\d:\d\d:\d\d\+00:00\n", out)


def test_bsdate_unix_timestamp(capsys: pytest.CaptureFixture[str]) -> None:
    # 1712966400 == 2024-04-13T00:00:00Z == BS 2081-01-01
    bsdate(["-u", "-Iseconds", "@1712966400"])
    assert capsys.readouterr().out == "2081-01-01T00:00:00+00:00\n"


def test_bsdate_double_dash_ends_options(capsys: pytest.CaptureFixture[str]) -> None:
    # As in GNU and BSD date: after "--", "-Iseconds" is a DATE, not an option.
    with pytest.raises(SystemExit):
        bsdate(["--", "-Iseconds"])
    assert "Invalid isoformat string: '-Iseconds'" in capsys.readouterr().err


def test_bsdate_plus_format_after_double_dash(
    capsys: pytest.CaptureFixture[str],
) -> None:
    bsdate(["--", "+%F", "2024-04-13"])
    assert capsys.readouterr().out == "2081-01-01\n"


def test_bsdate_colon_z(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["+%z %:z", "2024-04-13T12:00:00+05:45"])
    assert capsys.readouterr().out == "+0545 +05:45\n"


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["garbage"], "Invalid isoformat string"),
        (["@99999999999999999999"], "out of range"),
        (["1800-01-01"], "date 1800-01-01 outside"),
        (["-c", "2200-1-1"], r"year 2200 outside \[1970, 2100\]"),
        (["-c", "2081/1/1"], "expected YYYY-M-D"),
        (["-c", ""], "expected YYYY-M-D, got ''"),
        (["-c", "2081-01-01", "2024-04-13"], "-c/--from-bs and DATE are mutually"),
    ],
)
def test_bsdate_bad_input_is_a_usage_error(
    capsys: pytest.CaptureFixture[str], args: list[str], message: str
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        bsdate(args)
    assert exc_info.value.code == 2
    assert re.search(f"error: .*{message}", capsys.readouterr().err)


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["2200"], "year 2200 outside [1970, 2100]"),
        (["2080", "13"], "month 13 outside [1, 12]"),
        (["-f", "7", "2080"], "first-weekday 7 outside [0, 6]"),
        (["-m", "0", "2081"], "months 0 must be at least 1"),
    ],
)
def test_bscal_rejects_invalid_arguments(
    capsys: pytest.CaptureFixture[str], args: list[str], message: str
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cal(args)
    assert exc_info.value.code == 2
    assert message in capsys.readouterr().err


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cal(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip()


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        # Without an offset, DATE is read as UTC, as `date -u` does.
        (["-u", "-Iseconds", "2024-04-13T03:00"], "2081-01-01T03:00:00+00:00"),
        (["-u", "-I", "2024-04-13"], "2081-01-01"),
        # With an offset, it is converted to UTC.
        (["-u", "-Iseconds", "2024-04-13T03:00+05:45"], "2080-12-30T21:15:00+00:00"),
    ],
)
def test_bsdate_utc_input(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    args: list[str],
    expected: str,
) -> None:
    # A zone far from UTC, so reading the input as local time would show.
    monkeypatch.setenv("TZ", "Asia/Kathmandu")
    time.tzset()
    try:
        bsdate(args)
    finally:
        monkeypatch.undo()
        time.tzset()
    assert capsys.readouterr().out == expected + "\n"


@pytest.mark.parametrize(
    ("fmt", "expected"), [("+%^B %^b", "BAISAKH BAI"), ("+%e|%0e|%-e", " 1|01|1")]
)
def test_bsdate_gnu_flags(
    capsys: pytest.CaptureFixture[str], fmt: str, expected: str
) -> None:
    bsdate([fmt, "2024-04-13"])
    assert capsys.readouterr().out == expected + "\n"
