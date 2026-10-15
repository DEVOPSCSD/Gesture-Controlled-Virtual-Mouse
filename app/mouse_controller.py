
import pyautogui


class MouseController:
    def __init__(self, smoothing=0.3):
        self.screen_width, self.screen_height = pyautogui.size()
        self.smoothing = smoothing
        self.last_x = None
        self.last_y = None
        self.dragging = False

        # Prevent PyAutoGUI from moving into a corner and aborting.
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.02

    def move_cursor(self, x, y):
        """Convert normalized hand coordinates to screen coordinates."""
        # Keep the cursor away from screen edges.
        margin = 0.05
        x = max(margin, min(1 - margin, x))
        y = max(margin, min(1 - margin, y))

        target_x = int(x * (self.screen_width - 1))
        target_y = int(y * (self.screen_height - 1))

        # Smooth sudden movements.
        if self.last_x is None:
            self.last_x, self.last_y = target_x, target_y
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
        """Perform one left click."""
        if self.dragging:
            self.stop_drag()
        pyautogui.click(button="left")

    def right_click(self):
        """Perform one right click."""
        if self.dragging:
            self.stop_drag()
        pyautogui.click(button="right")

    def start_drag(self):
        """Hold the left mouse button for dragging."""
        if not self.dragging:
            pyautogui.mouseDown(button="left")
            self.dragging = True

    def stop_drag(self):
        """Release the left mouse button."""
        if self.dragging:
            pyautogui.mouseUp(button="left")
            self.dragging = False

    def release_all(self):
        """Release any held mouse button."""
        self.stop_drag()
