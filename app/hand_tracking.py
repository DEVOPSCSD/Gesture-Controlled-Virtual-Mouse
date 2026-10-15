
import cv2
import mediapipe as mp


class HandTracker:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def start(self):
        """Open the webcam."""
        if self.camera is not None and self.camera.isOpened():
            return True

        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            return False

        return True

    def get_frame(self):
        """
        Return:
        - annotated webcam frame
        - normalized hand landmarks, or None
        """
        if self.camera is None or not self.camera.isOpened():
            return None, None

        success, frame = self.camera.read()

        if not success:
            return None, None

        # Mirror the image for a natural webcam experience.
        frame = cv2.flip(frame, 1)

        # MediaPipe expects RGB input.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb_frame)

        landmarks = None

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            # Draw hand landmarks and connections.
            self.mp_draw.draw_landmarks(
                frame,
                hand,
                self.mp_hands.HAND_CONNECTIONS
            )

            landmarks = [
                {
                    "id": i,
                    "x": point.x,
                    "y": point.y,
                    "z": point.z
                }
                for i, point in enumerate(hand.landmark)
            ]

            # Display useful fingertip information.
            for tip_id, name in [
                (4, "Thumb"),
                (8, "Index"),
                (12, "Middle"),
                (16, "Ring"),
                (20, "Pinky")
            ]:
                point = hand.landmark[tip_id]

                height, width, _ = frame.shape
                px = int(point.x * width)
                py = int(point.y * height)

                cv2.circle(
                    frame, (px, py), 8, (0, 255, 0), -1
                )

                cv2.putText(
                    frame,
                    name,
                    (px + 5, py - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (0, 255, 0),
                    1
                )

        return frame, landmarks

    def stop(self):
        """Release the webcam and MediaPipe resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.hands.close()


if __name__ == "__main__":
    tracker = HandTracker()

    if not tracker.start():
        print("ERROR: Could not open webcam.")
        print("Check camera permissions and close other camera apps.")
    else:
        print("Webcam started. Press Q to quit.")

        try:
            while True:
                frame, landmarks = tracker.get_frame()

                if frame is None:
                    print("Could not read webcam frame.")
                    break

                if landmarks:
                    print(
                        "Index fingertip:",
                        landmarks[8]["x"],
                        landmarks[8]["y"]
                    )

                cv2.imshow("Virtual Mouse - Hand Tracking", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            tracker.stop()
            cv2.destroyAllWindows()
