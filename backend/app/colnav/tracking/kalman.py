
import numpy as np
from datetime import datetime


class KalmanFilterCV:

    """
    Constant Velocity Kalman Filter.

    State:
        [x, y, vx, vy]

    Measurement:
        [x, y]

    Coordinates and velocities are in image-plane units.
    """

    def __init__(
        self,
        process_noise=1.0,
        measurement_noise=10.0
    ):
        if process_noise <= 0:
            raise ValueError("process_noise must be positive")

        if measurement_noise <= 0:
            raise ValueError("measurement_noise must be positive")

        self.process_noise = process_noise
        self.measurement_noise = measurement_noise

        self.state = None
        self.covariance = None
        self.last_timestamp = None

        # Measurement matrix: observe x and y only
        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=float)

        self.R = np.eye(2) * measurement_noise

    def initialize(self, x, y, timestamp):
        self.state = np.array(
            [x, y, 0.0, 0.0],
            dtype=float
        )

        self.covariance = np.diag([
            10.0, 10.0, 100.0, 100.0
        ])

        self.last_timestamp = timestamp

        return self.get_state()

    def _transition_matrix(self, dt):
        return np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=float)

    def _process_noise_matrix(self, dt):
        q = self.process_noise

        block = np.array([
            [dt**4 / 4, dt**3 / 2],
            [dt**3 / 2, dt**2]
        ]) * q

        Q = np.zeros((4, 4), dtype=float)

        Q[np.ix_([0, 2], [0, 2])] = block
        Q[np.ix_([1, 3], [1, 3])] = block

        return Q

    def predict(self, timestamp):
        if self.state is None:
            raise RuntimeError("Kalman filter is not initialized")

        dt = (timestamp - self.last_timestamp).total_seconds()

        if dt < 0:
            raise ValueError("Timestamp cannot move backwards")

        if dt == 0:
            return self.get_state()

        F = self._transition_matrix(dt)
        Q = self._process_noise_matrix(dt)

        self.state = F @ self.state

        self.covariance = (
            F @ self.covariance @ F.T + Q
        )

        self.last_timestamp = timestamp

        return self.get_state()

    def update(self, x, y, timestamp):
        if self.state is None:
            return self.initialize(x, y, timestamp)

        # Predict state to the measurement timestamp
        self.predict(timestamp)

        measurement = np.array([x, y], dtype=float)

        innovation = (
            measurement - self.H @ self.state
        )

        S = (
            self.H @ self.covariance @ self.H.T
            + self.R
        )

        K = (
            self.covariance @ self.H.T
            @ np.linalg.inv(S)
        )

        self.state = (
            self.state + K @ innovation
        )

        # Joseph form covariance update
        identity = np.eye(4)
        residual = identity - K @ self.H

        self.covariance = (
            residual @ self.covariance @ residual.T
            + K @ self.R @ K.T
        )

        return self.get_state()

    def get_state(self):
        if self.state is None:
            return None

        return {
            "x": float(self.state[0]),
            "y": float(self.state[1]),
            "vx": float(self.state[2]),
            "vy": float(self.state[3]),
            "covariance": self.covariance.copy()
        }
