
import pytest

from app.colnav.tracking.movement import MovementClassifier


@pytest.fixture
def classifier():
    return MovementClassifier(velocity_threshold=5.0)


def test_classifies_right(classifier):
    assert classifier.classify(25.0, 4.0) == "right"


def test_classifies_left(classifier):
    assert classifier.classify(-30.0, 3.0) == "left"


def test_classifies_up(classifier):
    assert classifier.classify(2.0, -20.0) == "up"


def test_classifies_down(classifier):
    assert classifier.classify(3.0, 22.0) == "down"


def test_classifies_stationary(classifier):
    assert classifier.classify(1.0, 2.0) == "stationary"


def test_classifies_zero_velocity(classifier):
    assert classifier.classify(0.0, 0.0) == "stationary"


def test_returns_unknown_with_insufficient_observations(classifier):
    assert classifier.classify(25.0, 4.0, observation_count=1) == "unknown"


def test_rejects_negative_threshold():
    with pytest.raises(ValueError):
        MovementClassifier(velocity_threshold=-1.0)


def test_diagonal_movement_uses_dominant_axis(classifier):
    assert classifier.classify(20.0, 10.0) == "right"
    assert classifier.classify(10.0, -20.0) == "up"
