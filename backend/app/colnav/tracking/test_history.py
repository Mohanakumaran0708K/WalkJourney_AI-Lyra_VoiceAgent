
from datetime import datetime, timedelta

from app.colnav.schemas import DetectionResult, BoundingBox
from app.colnav.tracking.history import PositionHistory


def create_detection(track_id, x1, y1, x2, y2):
    return DetectionResult(
        object_id=track_id,
        class_name="person",
        confidence=0.95,
        bounding_box=BoundingBox(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2
        )
    )


def test_position_history_update():

    manager = PositionHistory()

    timestamp = datetime.now()

    detections = [
        create_detection(1, 100, 100, 200, 300)
    ]

    tracks = manager.update(detections, timestamp)

    assert len(tracks) == 1
    assert tracks[0].track_id == 1
    assert tracks[0].center_x == 150
    assert tracks[0].center_y == 200

    history = manager.get_history(1)

    assert len(history) == 1

    print("PASS: Position history update")


def test_multiple_pedestrian_ids():

    manager = PositionHistory()

    timestamp = datetime.now()

    detections = [
        create_detection(1, 100, 100, 200, 300),
        create_detection(2, 300, 100, 400, 300)
    ]

    manager.update(detections, timestamp)

    assert len(manager.get_history(1)) == 1
    assert len(manager.get_history(2)) == 1

    print("PASS: Multiple pedestrian IDs")


def test_bounded_history():

    manager = PositionHistory(max_history=3)

    timestamp = datetime.now()

    for i in range(5):

        detection = create_detection(
            1,
            100 + i,
            100,
            200 + i,
            300
        )

        manager.update(
            [detection],
            timestamp + timedelta(milliseconds=i * 100)
        )

    history = manager.get_history(1)

    assert len(history) == 3
    assert history[-1].center_x == 154

    print("PASS: Bounded position history")


def test_stale_track_removal():

    manager = PositionHistory(stale_timeout_seconds=2)

    timestamp = datetime.now()

    detection = create_detection(
        1, 100, 100, 200, 300
    )

    manager.update([detection], timestamp)

    assert len(manager.get_history(1)) == 1

    manager.remove_stale_tracks(
        timestamp + timedelta(seconds=3)
    )

    assert len(manager.get_history(1)) == 0

    print("PASS: Stale track removal")


def test_detection_without_track_id():

    manager = PositionHistory()

    timestamp = datetime.now()

    detection = create_detection(
        None, 100, 100, 200, 300
    )

    tracks = manager.update([detection], timestamp)

    assert len(tracks) == 0
    assert len(manager.histories) == 0

    print("PASS: Detection without track ID")


if __name__ == "__main__":

    test_position_history_update()
    test_multiple_pedestrian_ids()
    test_bounded_history()
    test_stale_track_removal()
    test_detection_without_track_id()

    print("\nAll position history tests passed!")
