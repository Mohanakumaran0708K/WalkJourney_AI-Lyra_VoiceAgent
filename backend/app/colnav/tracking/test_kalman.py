
from datetime import datetime, timedelta

import pytest

from app.colnav.tracking.kalman import KalmanFilterCV


def test_kalman_initialization():
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    kf = KalmanFilterCV()
    state = kf.initialize(100, 200, timestamp)

    assert state["x"] == 100
    assert state["y"] == 200
    assert state["vx"] == 0
    assert state["vy"] == 0


def test_stationary_pedestrian():
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    kf = KalmanFilterCV()

    kf.update(100, 200, timestamp)

    state = kf.update(
        100, 200,
        timestamp + timedelta(seconds=0.1)
    )

    assert abs(state["vx"]) < 1
    assert abs(state["vy"]) < 1


def test_moving_pedestrian():
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    kf = KalmanFilterCV()

    kf.update(100, 200, timestamp)

    state = None

    # Pedestrian moves 10 pixels horizontally
    # every 0.1 seconds.
    for i in range(1, 11):
        state = kf.update(
            100 + (i * 10),
            200,
            timestamp + timedelta(seconds=i * 0.1)
        )

    assert state["vx"] > 50
    assert abs(state["vy"]) < 5


def test_variable_frame_intervals():
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    kf = KalmanFilterCV()

    kf.update(100, 200, timestamp)

    state = kf.update(
        120, 200,
        timestamp + timedelta(seconds=0.2)
    )

    assert state["x"] > 100
    assert state["vx"] > 0


def test_rejects_backward_timestamp():
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    kf = KalmanFilterCV()
    kf.update(100, 200, timestamp)

    with pytest.raises(ValueError):
        kf.update(
            110, 200,
            timestamp - timedelta(seconds=0.1)
        )


def test_rejects_invalid_noise():
    with pytest.raises(ValueError):
        KalmanFilterCV(process_noise=0)

    with pytest.raises(ValueError):
        KalmanFilterCV(measurement_noise=-1)
