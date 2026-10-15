import math


class GestureController:
    """Recognize basic gestures from MediaPipe hand landmarks."""

    @staticmethod
    def distance(a, b):
        return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

    @staticmethod
    def finger_is_up(points, tip_id, pip_id):
        return points[tip_id]["y"] < points[pip_id]["y"]

    def recognize_gesture(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return "UNKNOWN"

        index_up = self.finger_is_up(landmarks, 8, 6)
        middle_up = self.finger_is_up(landmarks, 12, 10)
        ring_up = self.finger_is_up(landmarks, 16, 14)
        pinky_up = self.finger_is_up(landmarks, 20, 18)

        pinch_distance = self.distance(landmarks[4], landmarks[8])

        # A fist is detected before the pinch gesture.
        fist = not any([index_up, middle_up, ring_up, pinky_up])

        if fist:
            return "DRAG"

        # Pinch to left-click while at least one other finger is raised.
        if pinch_distance < 0.045 and (
            middle_up or ring_up or pinky_up
        ):
            return "LEFT_CLICK"

        # Raise index and middle fingers for right-click.
        if index_up and middle_up and not ring_up and not pinky_up:
            return "RIGHT_CLICK"

        # Raise only the index finger to move.
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "MOVE"

        return "UNKNOWN"
