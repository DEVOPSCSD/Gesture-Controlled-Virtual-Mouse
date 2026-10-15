from flask import Flask, render_template, request, jsonify
from threading import RLock

from app.mouse_controller import MouseController

app = Flask(__name__)

mouse = MouseController()
control_lock = RLock()
control_enabled = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start_control():
    global control_enabled

    with control_lock:
        control_enabled = True

    return jsonify(success=True, message="Gesture control started")


@app.route("/api/stop", methods=["POST"])
def stop_control():
    global control_enabled

    with control_lock:
        control_enabled = False
        mouse.release_all()

    return jsonify(success=True, message="Gesture control stopped")


@app.route("/api/gesture", methods=["POST"])
def handle_gesture():
    data = request.get_json(silent=True) or {}
    gesture = str(data.get("gesture", "UNKNOWN")).upper()

    allowed = {
        "MOVE", "DRAG", "LEFT_CLICK", "RIGHT_CLICK",
        "RELEASE_DRAG", "UNKNOWN"
    }

    if gesture not in allowed:
        return jsonify(success=False, error="Unsupported gesture"), 400

    with control_lock:
        if not control_enabled:
            return jsonify(success=False, error="Click START first"), 409

        try:
            if gesture in ("MOVE", "DRAG"):
                x = float(data["x"])
                y = float(data["y"])

                if not (0 <= x <= 1 and 0 <= y <= 1):
                    return jsonify(
                        success=False,
                        error="Coordinates must be between 0 and 1"
                    ), 400

                if gesture == "DRAG":
                    mouse.start_drag()
                    mouse.move_cursor(x, y)
                else:
                    mouse.stop_drag()
                    mouse.move_cursor(x, y)

            elif gesture == "LEFT_CLICK":
                mouse.left_click()

            elif gesture == "RIGHT_CLICK":
                mouse.right_click()

            elif gesture in ("RELEASE_DRAG", "UNKNOWN"):
                mouse.stop_drag()

        except Exception as error:
            app.logger.exception("Mouse action failed")
            mouse.release_all()
            return jsonify(success=False, error=str(error)), 500

    return jsonify(success=True, gesture=gesture)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
