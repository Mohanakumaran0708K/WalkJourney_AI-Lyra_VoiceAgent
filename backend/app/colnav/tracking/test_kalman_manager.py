
from datetime import datetime, timedelta

import pytest

from app.colnav.schemas import TrackingResult
from app.colnav.tracking.kalman_manager import KalmanFilterManager


def make_track(track_id, x, y):
    return TrackingResult(
        track_id=track_id,
        class_name="person",
        center_x=x,
        center_y=y,
        movement_status="unknown"
    )


def test_manager_creates_independent_filters():
    manager = KalmanFilterManager()
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    tracks = [
        make_track(7, 100, 200),
        make_track(12, 400, 300)
    ]

    results = manager.update(tracks, timestamp)

    assert len(results) == 2
    assert len(manager.filters) == 2
    assert manager.get_filter(7) is not manager.get_filter(12)


def test_manager_updates_existing_filter():
    manager = KalmanFilterManager()
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    manager.update(
        [make_track(7, 100, 200)],
        timestamp
    )

    original_filter = manager.get_filter(7)

    results = manager.update(
        [make_track(7, 120, 200)],
        timestamp + timedelta(seconds=0.2)
    )

    assert manager.get_filter(7) is original_filter
    assert len(results) == 1
    assert results[0].x > 100


def test_manager_predicts_missing_pedestrian():
    manager = KalmanFilterManager()
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    manager.update(
        [make_track(7, 100, 200)],
        timestamp
    )

    predictions = manager.predict_missing(
        timestamp + timedelta(seconds=0.1)
    )

    assert len(predictions) == 1
    assert predictions[0].track_id == 7
    assert predictions[0].status == "predicted"


def test_manager_removes_stale_filter():
    manager = KalmanFilterManager(
        stale_timeout_seconds=2.0
    )

    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    manager.update(
        [make_track(7, 100, 200)],
        timestamp
    )

    manager.remove_stale_filters(
        timestamp + timedelta(seconds=3)
    )

    assert manager.get_filter(7) is None
    assert 7 not in manager.last_seen


def test_manager_clear():
    manager = KalmanFilterManager()
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    manager.update(
        [make_track(7, 100, 200)],
        timestamp
    )

    manager.clear()

    assert len(manager.filters) == 0
    assert len(manager.last_seen) == 0


def test_manager_rejects_invalid_stale_timeout():
    with pytest.raises(ValueError):
        KalmanFilterManager(stale_timeout_seconds=0)


def test_manager_returns_pydantic_estimated_states():
    from app.colnav.schemas import EstimatedMotionState

    manager = KalmanFilterManager()
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    results = manager.update(
        [make_track(7, 100, 200)],
        timestamp
    )

    assert isinstance(results[0], EstimatedMotionState)
    assert results[0].track_id == 7
    assert results[0].class_name == "person"
    assert results[0].status == "observed"
    assert len(results[0].covariance) == 4
    assert all(len(row) == 4 for row in results[0].covariance)


def test_prediction_does_not_refresh_last_seen():
    manager = KalmanFilterManager()
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    manager.update(
        [make_track(7, 100, 200)],
        timestamp
    )

    original_last_seen = manager.last_seen[7]

    manager.predict_missing(
        timestamp + timedelta(seconds=0.5)
    )

    assert manager.last_seen[7] == original_last_seen


def test_prediction_skips_currently_observed_tracks():
    manager = KalmanFilterManager()
    timestamp = datetime(2026, 11, 14, 10, 0, 0)

    manager.update(
        [make_track(7, 100, 200)],
        timestamp
    )

    predictions = manager.predict_missing(
        timestamp + timedelta(seconds=0.1),
        observed_track_ids={7}
    )

    assert len(predictions) == 0
