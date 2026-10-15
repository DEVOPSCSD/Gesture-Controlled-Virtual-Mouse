
from app.gesture_controller import GestureController


def make_hand(index_up=False, middle_up=False,
              ring_up=False, pinky_up=False,
              pinch=False):
    """Create simple synthetic landmarks for testing."""

    landmarks = [
        {"id": i, "x": 0.5, "y": 0.5, "z": 0.0}
        for i in range(21)
    ]

    # Put finger tips above their joints when raised.
    finger_pairs = [
        (8, 6, index_up),
        (12, 10, middle_up),
        (16, 14, ring_up),
        (20, 18, pinky_up),
    ]

    for tip, joint, raised in finger_pairs:
        landmarks[tip]["y"] = 0.3 if raised else 0.7
        landmarks[joint]["y"] = 0.5

    # Default thumb and index tips are far apart.
    landmarks[4]["x"] = 0.3
    landmarks[4]["y"] = 0.5
    landmarks[8]["x"] = 0.6

    # Pinch: bring thumb and index tips close together.
    if pinch:
        landmarks[4]["x"] = landmarks[8]["x"]
        landmarks[4]["y"] = landmarks[8]["y"]

    return landmarks


def test_unknown_without_hand():
    controller = GestureController()
    assert controller.recognize_gesture(None) == "UNKNOWN"


def test_move():
    controller = GestureController()
    hand = make_hand(index_up=True)
    assert controller.recognize_gesture(hand) == "MOVE"


def test_right_click():
    controller = GestureController()
    hand = make_hand(index_up=True, middle_up=True)
    assert controller.recognize_gesture(hand) == "RIGHT_CLICK"


def test_drag():
    controller = GestureController()
    hand = make_hand()
    assert controller.recognize_gesture(hand) == "DRAG"


def test_left_click():
    controller = GestureController()
    hand = make_hand(pinch=True)
    assert controller.recognize_gesture(hand) == "LEFT_CLICK"
