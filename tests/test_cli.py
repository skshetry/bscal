import pytest

from bscal import cal

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
