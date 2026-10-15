
from unittest.mock import patch
from app.mouse_controller import MouseController


@patch("app.mouse_controller.pyautogui.moveTo")
def test_move_cursor(mock_move):
    mouse = MouseController()
    mouse.move_cursor(0.5, 0.5)

    mock_move.assert_called_once()


@patch("app.mouse_controller.pyautogui.click")
def test_left_click(mock_click):
    mouse = MouseController()
    mouse.left_click()

    mock_click.assert_called_once_with(button="left")


@patch("app.mouse_controller.pyautogui.click")
def test_right_click(mock_click):
    mouse = MouseController()
    mouse.right_click()

    mock_click.assert_called_once_with(button="right")


@patch("app.mouse_controller.pyautogui.mouseDown")
def test_start_drag(mock_down):
    mouse = MouseController()
    mouse.start_drag()
    mouse.start_drag()

    mock_down.assert_called_once_with(button="left")
    assert mouse.dragging is True


@patch("app.mouse_controller.pyautogui.mouseUp")
def test_stop_drag(mock_up):
    mouse = MouseController()
    mouse.start_drag()
    mouse.stop_drag()

    mock_up.assert_called_once_with(button="left")
    assert mouse.dragging is False
