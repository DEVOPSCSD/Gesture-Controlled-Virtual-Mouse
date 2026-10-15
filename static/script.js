const startButton = document.getElementById("start-btn");
const stopButton = document.getElementById("stop-btn");

const gestureText = document.getElementById("gesture");
const mouseStatus = document.getElementById("mouse-status");

const systemStatus = document.getElementById("system-status");
const systemDot = document.getElementById("system-dot");

const cameraStatus = document.getElementById("camera-status");

const cameraPlaceholder =
    document.getElementById("camera-placeholder");

const video =
    document.getElementById("video");


/* START BUTTON */

startButton.addEventListener("click", function () {

    gestureText.textContent = "Ready";
    mouseStatus.textContent = "Running";

    systemStatus.textContent = "System Online";
    systemDot.style.background = "#16a34a";

    cameraStatus.textContent = "Camera Starting...";

    cameraPlaceholder.style.display = "flex";

});


/* STOP BUTTON */

stopButton.addEventListener("click", function () {

    gestureText.textContent = "Waiting...";
    mouseStatus.textContent = "Stopped";

    systemStatus.textContent = "System Offline";
    systemDot.style.background = "#9ca3af";

    cameraStatus.textContent = "Camera Off";

    cameraPlaceholder.style.display = "flex";

    video.style.display = "none";

});