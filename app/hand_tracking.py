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
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def start(self):
        if self.camera is not None and self.camera.isOpened():
            return True

        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            return False

        return True

    def get_frame(self):
        if self.camera is None or not self.camera.isOpened():
            return None, None

        success, frame = self.camera.read()

        if not success:
            return None, None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        landmarks = None

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            self.mp_draw.draw_landmarks(
                frame, hand, self.mp_hands.HAND_CONNECTIONS
            )

            landmarks = [
                {
                    "id": i,
                    "x": float(p.x),
                    "y": float(p.y),
                    "z": float(p.z)
                }
                for i, p in enumerate(hand.landmark)
            ]

            cv2.putText(
                frame, "HAND DETECTED", (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 255, 0), 2
            )
        else:
            cv2.putText(
                frame, "NO HAND DETECTED", (15, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (0, 0, 255), 2
            )

        return frame, landmarks

    def stop(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.hands.close()


if __name__ == "__main__":
    tracker = HandTracker()

    try:
        if not tracker.start():
            print("Could not open webcam.")
        else:
            print("Move your hand in front of the camera. Press Q to quit.")

            while True:
                frame, landmarks = tracker.get_frame()

                if frame is None:
                    break

                if landmarks:
                    print(
                        "Index:",
                        round(landmarks[8]["x"], 3),
                        round(landmarks[8]["y"], 3)
                    )

                cv2.imshow("Hand Tracking Test", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        tracker.stop()
        cv2.destroyAllWindows()