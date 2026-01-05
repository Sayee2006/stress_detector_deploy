let stream = null;
let frameInterval = null;
let timerInterval = null;

let stressSamples = [];
let timeLeft = 30;

const video = document.getElementById("video");
const stressValue = document.getElementById("stressValue");
const suggestion = document.getElementById("suggestion");
const lastCheck = document.getElementById("lastCheck");
const avgStress = document.getElementById("avgStress");

document.getElementById("startBtn").onclick = async () => {
  stressSamples = [];
  timeLeft = 30;

  stressValue.innerText = "Measuring...";
  suggestion.innerText = "Stay relaxed 😌";

  stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;
  video.play();

  frameInterval = setInterval(captureFrame, 2000);
  timerInterval = setInterval(updateTimer, 1000);
};

document.getElementById("stopBtn").onclick = stopAnalysis;

function updateTimer() {
  timeLeft--;
  suggestion.innerText = `Analyzing... ${timeLeft}s`;

  if (timeLeft <= 0) stopAnalysis();
}

async function captureFrame() {
  const res = await fetch("/predict", { method: "POST" });
  const data = await res.json();

  if (data.stress) stressSamples.push(data.stress);
}

function stopAnalysis() {
  clearInterval(frameInterval);
  clearInterval(timerInterval);

  if (stream) stream.getTracks().forEach(t => t.stop());

  if (stressSamples.length === 0) {
    stressValue.innerText = "--";
    suggestion.innerText = "No data captured ❌";
    return;
  }

  const finalStress = Math.round(
    stressSamples.reduce((a, b) => a + b) / stressSamples.length
  );

  stressValue.innerText = finalStress + "%";
  lastCheck.innerText = new Date().toLocaleString();

  if (finalStress <= 45) {
    suggestion.innerText = "You look relaxed 😄";
    stressValue.style.background = "#1b5e20";
  } else if (finalStress <= 70) {
    suggestion.innerText = "Moderate stress 🙂 Try breathing";
    stressValue.style.background = "#f9a825";
  } else {
    suggestion.innerText = "High stress 😟 Relax now";
    stressValue.style.background = "#b71c1c";
  }

  saveResult(finalStress);
}

async function saveResult(stress) {
  await fetch("/save_today", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ stress })
  });
  loadStats();
}

async function loadStats() {
  const res = await fetch("/stats");
  const data = await res.json();

  avgStress.innerText = data.avg === "--" ? "--" : data.avg + "%";
  lastCheck.innerText = data.last;
}

loadStats();
