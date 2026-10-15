const startButton = document.getElementById("start-btn");
const stopButton = document.getElementById("stop-btn");
const gestureText = document.getElementById("gesture");
const mouseStatus = document.getElementById("mouse-status");
const systemStatus = document.getElementById("system-status");
const systemDot = document.getElementById("system-dot");
const cameraStatus = document.getElementById("camera-status");
const cameraPlaceholder = document.getElementById("camera-placeholder");
const video = document.getElementById("video");

let stream = null;
let hands = null;
let running = false;
let sendingAction = false;
let lastSent = 0;
let lastClickTime = 0;
let previousGesture = "UNKNOWN";

const MOVE_INTERVAL = 60;
const CLICK_COOLDOWN = 450;

async function api(path, body = {}) {
    const response = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.error || `Request failed: ${response.status}`);
    }

    return result;
}

function fingerUp(points, tip, pip) {
    return points[tip].y < points[pip].y;
}

function detectGesture(points) {
    if (!points || points.length < 21) return "UNKNOWN";

    const indexUp = fingerUp(points, 8, 6);
    const middleUp = fingerUp(points, 12, 10);
    const ringUp = fingerUp(points, 16, 14);
    const pinkyUp = fingerUp(points, 20, 18);

    const pinchDistance = Math.hypot(
        points[4].x - points[8].x,
        points[4].y - points[8].y
    );

    // Closed fist: drag.
    const fist =
        !indexUp && !middleUp && !ringUp && !pinkyUp;

    if (fist) return "DRAG";

    // Pinch with at least one other finger raised: left click.
    if (
        pinchDistance < 0.045 &&
        (middleUp || ringUp || pinkyUp)
    ) {
        return "LEFT_CLICK";
    }

    // Index and middle raised: right click.
    if (indexUp && middleUp && !ringUp && !pinkyUp) {
        return "RIGHT_CLICK";
    }

    // Only index raised: move.
    if (indexUp && !middleUp && !ringUp && !pinkyUp) {
        return "MOVE";
    }

    return "UNKNOWN";
}

async function sendGesture(gesture, x, y) {
    const payload = { gesture };

    if (gesture === "MOVE" || gesture === "DRAG") {
        payload.x = x;
        payload.y = y;
    }

    return api("/api/gesture", payload);
}

function setMouseStatus(gesture) {
    const labels = {
        MOVE: "Mouse moving",
        DRAG: "Drag active - button held",
        LEFT_CLICK: "Left click",
        RIGHT_CLICK: "Right click",
        RELEASE_DRAG: "Drag released",
        UNKNOWN: "Waiting for gesture"
    };

    mouseStatus.textContent = labels[gesture] || gesture;
}

async function sendAction(gesture, x, y) {
    if (!running || sendingAction) return;

    sendingAction = true;

    try {
        await sendGesture(gesture, x, y);
        setMouseStatus(gesture);
    } catch (error) {
        console.error("Mouse API error:", error);
        mouseStatus.textContent = "Control error: " + error.message;
    } finally {
        sendingAction = false;
    }
}

function handleResults(results) {
    if (!running) return;

    const points = results.multiHandLandmarks?.[0];

    if (!points) {
        gestureText.textContent = "No hand detected";
        cameraStatus.textContent = "Camera On - No Hand";

        if (previousGesture === "DRAG") {
            previousGesture = "UNKNOWN";
            sendAction("RELEASE_DRAG");
        }

        return;
    }

    cameraStatus.textContent = "Hand Detected";

    const gesture = detectGesture(points);
    gestureText.textContent = gesture;

    console.log("Gesture:", gesture);

    const indexTip = points[8];

    // The preview is mirrored. This coordinate mapping is for a
    // mirrored-control experience; reverse X only if movement is wrong.
    const x = Math.max(0, Math.min(1, 1 - indexTip.x));
    const y = Math.max(0, Math.min(1, indexTip.y));

    const now = Date.now();
    const previous = previousGesture;

    // Release a drag as soon as the fist opens or changes.
    if (previous === "DRAG" && gesture !== "DRAG") {
        previousGesture = gesture;
        sendAction("RELEASE_DRAG");

        // A click gesture that follows the release will be processed
        // on the next frame if the user holds it.
        return;
    }

    previousGesture = gesture;

    // Movement and drag need continuous coordinate updates.
    if (gesture === "MOVE" || gesture === "DRAG") {
        if (!sendingAction && now - lastSent >= MOVE_INTERVAL) {
            lastSent = now;
            sendAction(gesture, x, y);
        }
        return;
    }

    // Click once per gesture, with a cooldown.
    if (
        gesture === "LEFT_CLICK" &&
        previous !== "LEFT_CLICK" &&
        now - lastClickTime >= CLICK_COOLDOWN
    ) {
        lastClickTime = now;
        sendAction("LEFT_CLICK");
    } else if (
        gesture === "RIGHT_CLICK" &&
        previous !== "RIGHT_CLICK" &&
        now - lastClickTime >= CLICK_COOLDOWN
    ) {
        lastClickTime = now;
        sendAction("RIGHT_CLICK");
    } else if (gesture === "UNKNOWN" && !sendingAction) {
        setMouseStatus("UNKNOWN");
    }
}

async function processFrame() {
    if (!running || !hands) return;

    try {
        if (video.readyState >= 2) {
            await hands.send({ image: video });
        }
    } catch (error) {
        console.error("MediaPipe frame error:", error);
        gestureText.textContent = "Detection error";
    }

    if (running) {
        requestAnimationFrame(processFrame);
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    video.pause();
    video.srcObject = null;
    video.style.display = "none";
    cameraPlaceholder.style.display = "flex";
}

async function stopMouse() {
    running = false;

    try {
        if (hands) {
            await hands.close();
            hands = null;
        }
    } catch (error) {
        console.error("Detector shutdown error:", error);
    }

    stopCamera();

    try {
        await api("/api/stop");
    } catch (error) {
        console.error("Stop error:", error);
    }

    previousGesture = "UNKNOWN";
    gestureText.textContent = "Waiting...";
    cameraStatus.textContent = "Camera Off";
    mouseStatus.textContent = "Stopped";
    systemStatus.textContent = "System Offline";
    systemDot.style.background = "#9ca3af";

    startButton.disabled = false;
    stopButton.disabled = false;
}

startButton.addEventListener("click", async () => {
    if (running) return;

    startButton.disabled = true;
    gestureText.textContent = "Starting...";

    try {
        if (typeof window.Hands !== "function") {
            throw new Error("MediaPipe did not load. Check your internet connection.");
        }

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "user",
                width: { ideal: 640 },
                height: { ideal: 480 }
            },
            audio: false
        });

        video.srcObject = stream;
        video.style.display = "block";
        cameraPlaceholder.style.display = "none";

        await video.play();

        hands = new window.Hands({
            locateFile: file =>
                `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
        });

        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 1,
            minDetectionConfidence: 0.6,
            minTrackingConfidence: 0.6
        });

        hands.onResults(handleResults);

        await api("/api/start");

        running = true;
        sendingAction = false;
        previousGesture = "UNKNOWN";
        lastSent = 0;

        cameraStatus.textContent = "Camera On";
        mouseStatus.textContent = "Waiting for hand";
        systemStatus.textContent = "System Online";
        systemDot.style.background = "#16a34a";
        gestureText.textContent = "Detecting hand...";

        stopButton.disabled = false;
        requestAnimationFrame(processFrame);
    } catch (error) {
        console.error("Start error:", error);

        gestureText.textContent = "Start failed";
        mouseStatus.textContent = error.message;
        cameraStatus.textContent = "Camera Error";

        running = false;
        stopCamera();

        if (hands) {
            try {
                await hands.close();
            } catch (_) {}
            hands = null;
        }

        try {
            await api("/api/stop");
        } catch (_) {}

        startButton.disabled = false;
        systemStatus.textContent = "System Offline";
        systemDot.style.background = "#9ca3af";
    }
});

stopButton.addEventListener("click", stopMouse);

window.addEventListener("pagehide", () => {
    running = false;

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});