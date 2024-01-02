## Bikram Sambat Calendar

### Installation

1. Using pip
```console
pip install bscal
```

2. Using pipx

```console
pipx install bscal
```

### Usage


#### Display calendar in BS format

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

> [!TIP]
> You can provide `year` to display a calendar for that year, and also optionally specify the `month` for a specific month's calendar.

#### Display the current BS date:

```console
$ bsdate
Tue Poush 17 09:14:14 +0545 2080
```

#### Display a specific date (from given ISO format)

```console
$ bsdate 2016-09-08
Thu Bhadra 23 09:17:21 +0545 2073
```

#### Display a specific date (represented as a Unix timestamp):

```console
$ bsdate 1473305798
Thu Bhadra 23 09:21:38 +0545 2073
```

#### Convert BS date to AD format

```console
$ bsdate -c 2073-05-23
Thu Sep  8 09:19:00 +0545 2016
```