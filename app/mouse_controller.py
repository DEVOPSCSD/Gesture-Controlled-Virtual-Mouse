import pyautogui


class MouseController:
    def __init__(self, smoothing=0.35):
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothing = smoothing
        self.last_x = None
        self.last_y = None
        self.dragging = False

        # Moving the pointer to a screen corner triggers PyAutoGUI's failsafe.
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01

    def move_cursor(self, x, y):
        """Move the cursor using normalized coordinates from 0 to 1."""
        x = max(0.0, min(1.0, float(x)))
        y = max(0.0, min(1.0, float(y)))

        target_x = int(x * (self.screen_width - 1))
        target_y = int(y * (self.screen_height - 1))

        if self.last_x is None:
            self.last_x = target_x
            self.last_y = target_y
        else:
            self.last_x = int(
                self.smoothing * target_x
                + (1 - self.smoothing) * self.last_x
            )
            self.last_y = int(
                self.smoothing * target_y
                + (1 - self.smoothing) * self.last_y
            )

        pyautogui.moveTo(self.last_x, self.last_y)

    def left_click(self):
        self.stop_drag()
        pyautogui.click(button="left")

    def right_click(self):
        self.stop_drag()
        pyautogui.click(button="right")

    def start_drag(self):
        if not self.dragging:
            pyautogui.mouseDown(button="left")
            self.dragging = True

    def stop_drag(self):
        if self.dragging:
            try:
                pyautogui.mouseUp(button="left")
            finally:
                self.dragging = False

    def release_all(self):
        """Release any held mouse buttons."""
        try:
            self.stop_drag()
        finally:
            self.dragging = False
            pyautogui.mouseUp(button="left")
            pyautogui.mouseUp(button="right")
