import pytest
from datetime import time
from public_transport import get_morning_departures


@pytest.mark.parametrize(
    "time_outside_morning_commute",
    [
        time(hour=6, minute=59),
        time(hour=11, minute=0),
        time(hour=14, minute=30),
        time(hour=23, minute=0),
    ],
)
def test_returns_no_departures_outside_morning_hours(time_outside_morning_commute):
    departures = get_morning_departures(now=time_outside_morning_commute)

    assert departures == []
