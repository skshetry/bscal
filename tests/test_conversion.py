from hypothesis import given
from hypothesis.strategies import dates

from bscal import ad_to_bs, bs_to_ad, new_years


@given(dates(min(new_years.values()), max(new_years.values())))
def test(date):
    assert bs_to_ad(*ad_to_bs(date)) == date
