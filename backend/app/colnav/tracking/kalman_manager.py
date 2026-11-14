
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from app.colnav.schemas import (
    EstimatedMotionState,
    TrackingResult
)
from app.colnav.tracking.kalman import KalmanFilterCV


class KalmanFilterManager:

    def __init__(
        self,
        process_noise: float = 1.0,
        measurement_noise: float = 10.0,
        stale_timeout_seconds: float = 2.0
    ):
        if stale_timeout_seconds <= 0:
            raise ValueError("stale_timeout_seconds must be positive")

        self.process_noise = process_noise
        self.measurement_noise = measurement_noise

        self.stale_timeout = timedelta(
            seconds=stale_timeout_seconds
        )

        self.filters: Dict[int, KalmanFilterCV] = {}
        self.last_seen: Dict[int, datetime] = {}
        self.track_classes: Dict[int, str] = {}

    def update(
        self,
        tracks: List[TrackingResult],
        timestamp: datetime
    ) -> List[EstimatedMotionState]:

        estimated_states = []

        for track in tracks:
            track_id = track.track_id

            if track_id not in self.filters:
                self.filters[track_id] = KalmanFilterCV(
                    process_noise=self.process_noise,
                    measurement_noise=self.measurement_noise
                )

            kalman_filter = self.filters[track_id]

            state = kalman_filter.update(
                x=track.center_x,
                y=track.center_y,
                timestamp=timestamp
            )

            self.last_seen[track_id] = timestamp
            self.track_classes[track_id] = track.class_name

            estimated_states.append(
                EstimatedMotionState(
                    track_id=track_id,
                    class_name=track.class_name,
                    x=state["x"],
                    y=state["y"],
                    vx=state["vx"],
                    vy=state["vy"],
                    covariance=state["covariance"].tolist(),
                    status="observed"
                )
            )

        self.remove_stale_filters(timestamp)

        return estimated_states

    def predict_missing(
        self,
        timestamp: datetime,
        observed_track_ids: Optional[Set[int]] = None
    ) -> List[EstimatedMotionState]:

        observed_track_ids = observed_track_ids or set()

        self.remove_stale_filters(timestamp)

        predictions = []

        for track_id, kalman_filter in self.filters.items():

            # Do not predict pedestrians already observed
            # in the current frame.
            if track_id in observed_track_ids:
                continue

            last_seen = self.last_seen[track_id]

            age = (
                timestamp - last_seen
            ).total_seconds()

            if age < 0:
                raise ValueError(
                    "Timestamp cannot move backwards"
                )

            if age > self.stale_timeout.total_seconds():
                continue

            state = kalman_filter.predict(timestamp)

            predictions.append(
                EstimatedMotionState(
                    track_id=track_id,
                    class_name=self.track_classes[track_id],
                    x=state["x"],
                    y=state["y"],
                    vx=state["vx"],
                    vy=state["vy"],
                    covariance=state["covariance"].tolist(),
                    status="predicted"
                )
            )

        return predictions

    def remove_stale_filters(self, timestamp: datetime):

        stale_ids = [
            track_id
            for track_id, last_seen in self.last_seen.items()
            if timestamp - last_seen > self.stale_timeout
        ]

        for track_id in stale_ids:
            self.filters.pop(track_id, None)
            self.last_seen.pop(track_id, None)
            self.track_classes.pop(track_id, None)

    def get_filter(
        self,
        track_id: int
    ) -> Optional[KalmanFilterCV]:

        return self.filters.get(track_id)

    def clear(self):
        self.filters.clear()
        self.last_seen.clear()
        self.track_classes.clear()
