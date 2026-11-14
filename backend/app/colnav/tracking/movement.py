
from typing import Literal

MovementDirection = Literal[
    "left",
    "right",
    "up",
    "down",
    "stationary",
    "unknown",
]


class MovementClassifier:
    """
    Classifies pedestrian movement in image-plane coordinates.

    Coordinate convention:
        +X = right
        -X = left
        +Y = down
        -Y = up

    Velocity units are pixels per second.
    """

    def __init__(self, velocity_threshold: float = 5.0):
        if velocity_threshold < 0:
            raise ValueError("velocity_threshold cannot be negative")

        self.velocity_threshold = velocity_threshold

    def classify(
        self,
        vx: float,
        vy: float,
        observation_count: int = 2,
    ) -> MovementDirection:

        if observation_count < 2:
            return "unknown"

        threshold = self.velocity_threshold

        if abs(vx) <= threshold and abs(vy) <= threshold:
            return "stationary"

        # Select the dominant movement axis.
        if abs(vx) >= abs(vy):
            return "right" if vx > 0 else "left"

        return "down" if vy > 0 else "up"
