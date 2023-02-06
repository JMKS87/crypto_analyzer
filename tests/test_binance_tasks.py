from datetime import timedelta

import pytest

from charts.misc import interval_to_timedelta


# TODO: imports not working
@pytest.mark.parametrize(
    "interval, expected",
    [
        ("5m", timedelta(minutes=5)),
        ("1m", timedelta(minutes=1)),
        ("1h", timedelta(hours=1)),
        ("1d", timedelta(days=1)),
        ("2w", timedelta(weeks=2)),
    ],
)
def test_interval_to_timedelta(interval, expected):
    # given (via parameters)

    # when
    result = interval_to_timedelta(interval)

    # then
    assert result == expected
