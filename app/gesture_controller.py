
import math


class GestureController:
    """Recognize hand gestures from MediaPipe landmarks."""

    @staticmethod
    def distance(point1, point2):
        """Calculate distance between two normalized landmarks."""
        return math.hypot(
            point1["x"] - point2["x"],
            point1["y"] - point2["y"]
        )

    @staticmethod
    def finger_is_up(landmarks, tip_id, pip_id):
        """
        Check whether a finger is raised.
        Works best when the palm faces the camera.
        """
        return landmarks[tip_id]["y"] < landmarks[pip_id]["y"]

    def recognize_gesture(self, landmarks):
        """
        Input: list of 21 landmarks from hand_tracking.py
        Output: MOVE, LEFT_CLICK, RIGHT_CLICK, DRAG, UNKNOWN
        """

        if not landmarks or len(landmarks) < 21:
            return "UNKNOWN"

        # Check which fingers are raised.
        index_up = self.finger_is_up(landmarks, 8, 6)
        middle_up = self.finger_is_up(landmarks, 12, 10)
        ring_up = self.finger_is_up(landmarks, 16, 14)
        pinky_up = self.finger_is_up(landmarks, 20, 18)

        # Distance between thumb tip (4) and index tip (8).
        pinch_distance = self.distance(
            landmarks[4], landmarks[8]
        )

        # 1. Pinch: left click.
        if pinch_distance < 0.05:
            return "LEFT_CLICK"

        # 2. Index and middle fingers raised: right click.
        if (
            index_up and middle_up
            and not ring_up and not pinky_up
        ):
            return "RIGHT_CLICK"

        # 3. Only index finger raised: move cursor.
        if (
            index_up and not middle_up
            and not ring_up and not pinky_up
        ):
            return "MOVE"

        # 4. All four non-thumb fingers folded: drag.
        if not any([index_up, middle_up, ring_up, pinky_up]):
            return "DRAG"

        # 5. Any other pose.
        return "UNKNOWN"
