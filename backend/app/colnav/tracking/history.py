
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Optional

from app.colnav.schemas import DetectionResult, TrackingResult


@dataclass
class PositionObservation:
    timestamp: datetime
    center_x: float
    center_y: float


class PositionHistory:

    def __init__(
        self,
        max_history: int = 30,
        stale_timeout_seconds: float = 2.0
    ):
        if max_history < 2:
            raise ValueError("max_history must be at least 2")

        if stale_timeout_seconds <= 0:
            raise ValueError("stale_timeout_seconds must be positive")

        self.max_history = max_history
        self.stale_timeout = timedelta(
            seconds=stale_timeout_seconds
        )

        self.histories: Dict[
            int, Deque[PositionObservation]
        ] = defaultdict(
            lambda: deque(maxlen=self.max_history)
        )

        self.last_seen: Dict[int, datetime] = {}

    @staticmethod
    def get_center(detection: DetectionResult):
        box = detection.bounding_box

        center_x = (box.x1 + box.x2) / 2
        center_y = (box.y1 + box.y2) / 2

        return center_x, center_y

    def update(
        self,
        detections: List[DetectionResult],
        timestamp: datetime
    ) -> List[TrackingResult]:

        current_tracks = []

        for detection in detections:

            track_id = detection.object_id

            # Ignore detections without a valid tracker ID.
            if track_id is None:
                continue

            center_x, center_y = self.get_center(detection)

            observation = PositionObservation(
                timestamp=timestamp,
                center_x=center_x,
                center_y=center_y
            )

            self.histories[track_id].append(observation)
            self.last_seen[track_id] = timestamp

            current_tracks.append(
                TrackingResult(
                    track_id=track_id,
                    class_name=detection.class_name,
                    center_x=center_x,
                    center_y=center_y,
                    movement_status="unknown"
                )
            )

        self.remove_stale_tracks(timestamp)

        return current_tracks

    def remove_stale_tracks(self, timestamp: datetime):

        stale_ids = [
            track_id
            for track_id, last_seen in self.last_seen.items()
            if timestamp - last_seen > self.stale_timeout
        ]

        for track_id in stale_ids:
            self.histories.pop(track_id, None)
            self.last_seen.pop(track_id, None)

    def get_history(
        self,
        track_id: int
    ) -> List[PositionObservation]:

        return list(self.histories.get(track_id, []))

    def clear(self):
        self.histories.clear()
        self.last_seen.clear()
