import pytest

from bscal.bsdate import bsconv
from bscal.bsdate import main as bsdate
from bscal.cal import _CLICalendar as CLICalendar
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
def test_cli(
    capsys: pytest.CaptureFixture[str],
    args: tuple[str, str],
    expected: str,
) -> None:
    cal(args)
    out, err = capsys.readouterr()
    assert out == expected
    assert not err


def test_month_view_highlights_target_day_only() -> None:
    out = CLICalendar(highlight_day=(2080, 9, 5), firstweekday=6).formatmonth(2080, 9)
    assert f"{HIGHLIGHT} 5{RESET}" in out
    assert out.count(HIGHLIGHT) == 1


def test_year_view_highlights_only_in_target_month() -> None:
    # Day 5 also exists in every other month — verify only Poush 5 is highlighted.
    out = CLICalendar(highlight_day=(2080, 9, 5), firstweekday=6).formatyear(2080)
    assert out.count(HIGHLIGHT) == 1
    assert f"{HIGHLIGHT} 5{RESET}" in out


def test_no_highlight_when_unset() -> None:
    out = CLICalendar(highlight_day=None, firstweekday=6).formatmonth(2080, 9)
    assert HIGHLIGHT not in out


# AD 2024-04-13 == BS 2081-01-01 (Baisakh 1, a Saturday)


def test_bsdate_iso_date(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["2024-04-13"])
    parts = capsys.readouterr().out.split()
    assert parts[0] == "Sat"
    assert parts[1] == "Baisakh"
    assert parts[2] == "1"
    assert parts[-1] == "2081"


def test_bsdate_iso_datetime(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["2024-04-13T12:00:00"])
    parts = capsys.readouterr().out.split()
    assert parts[0] == "Sat"
    assert parts[1] == "Baisakh"
    assert parts[2] == "1"
    assert parts[3] == "12:00:00"
    assert parts[-1] == "2081"


def test_bsdate_convert_bs_to_ad(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-c", "2081-01-01"])
    parts = capsys.readouterr().out.split()
    assert parts[0] == "Sat"
    assert parts[1] == "Apr"
    assert parts[2] == "13"
    assert parts[-1] == "2024"


def test_bsconv(capsys: pytest.CaptureFixture[str]) -> None:
    bsconv("2081-01-01")
    parts = capsys.readouterr().out.split()
    assert parts[0] == "Sat"
    assert parts[1] == "Apr"
    assert parts[2] == "13"
    assert parts[-1] == "2024"


# GNU/BSD date(1) compatibility


def test_bsdate_iso_8601_short(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-I", "2024-04-13T12:34:56"])
    assert capsys.readouterr().out == "2081-01-01\n"


def test_bsdate_iso_8601_attached_seconds(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["-Iseconds", "2024-04-13T12:34:56+05:45"])
    assert capsys.readouterr().out == "2081-01-01T12:34:56+0545\n"


def test_bsdate_iso_8601_long_form(capsys: pytest.CaptureFixture[str]) -> None:
    bsdate(["--iso-8601=hours", "2024-04-13T12:34:56+05:45"])
    assert capsys.readouterr().out == "2081-01-01T12+0545\n"


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
    assert capsys.readouterr().out == "2081-01-01T06:49:56+0000\n"


def test_bsdate_invalid_iso_fmt() -> None:
    with pytest.raises(SystemExit):
        bsdate(["-Inanos", "2024-04-13"])


def test_bsdate_format_modes_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        bsdate(["+%F", "-I", "2024-04-13"])
