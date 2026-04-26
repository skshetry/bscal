## Bikram Sambat Calendar

### Installation

```console
pip install bscal     # or: pipx install bscal
```

### `bscal`

```console
$ bscal
     Poush 2080
Su Mo Tu We Th Fr Sa
 1  2  3  4  5  6  7
 8  9 10 11 12 13 14
15 16 17 18 19 20 21
22 23 24 25 26 27 28
29
```

Pass `year` for a year view, `year month` for a single month.

### `bsdate`

```console
$ bsdate                          # now
Tue Poush 17 09:14:14 +0545 2080

$ bsdate 2016-09-08               # AD date
Thu Bhadra 23 09:17:21 +0545 2073

$ bsdate 1473305798               # unix timestamp
Thu Bhadra 23 09:21:38 +0545 2073

$ bsdate -c 2073-05-23            # BS to AD
Thu Sep  8 09:19:00 +0545 2016
```

Flags: `-I[FMT]` for ISO 8601 (`date|hours|minutes|seconds`), `+FORMAT` for
BS-aware strftime, `-u` for UTC.

### Python

`BSDate` is a `datetime.date` for Bikram Sambat. Same constructors,
accessors, arithmetic, ordering. `strftime` tokens are BS-aware.

```python
from datetime import date
from bscal import BSDate, bs_to_ad, ad_to_bs

BSDate.today()
BSDate.fromisoformat("2081-01-01")
BSDate.from_ad(date(2024, 4, 13)).to_ad()

bs_to_ad(2081, 1, 1)         # (y, m, d) -> date
ad_to_bs(date(2024, 4, 13))  # date -> (y, m, d)
```

`bscal.cal` is the stdlib `calendar` for BS: `isleap`, `leapdays`,
`weekday`, `monthrange`, `month_name`, `month_abbr`, and a `BSCalendar`
(subclass of `calendar.TextCalendar`).
