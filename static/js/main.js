const latestUrl = "/api/latest";
const historyUrl = "/api/history";
const logEl = document.getElementById("logEntries");

async function fetchLatest() {
  try {
    const res = await fetch(latestUrl);
    const payload = await res.json();
    if (payload.status === "success") {
      const d = payload.data;
      document.getElementById("temp").innerText = Number(d.temperature).toFixed(1);
      document.getElementById("hum").innerText = Number(d.humidity).toFixed(1);
      document.getElementById("gas").innerText = Number(d.gas).toFixed(0);

      // prediction object: {risk, probability, method}
      const pred = d.prediction || {risk: "--", probability: 0};
      const percent = Math.round(pred.probability * 100);
      document.getElementById("risk").innerText = pred.risk;
      document.getElementById("risk_percent").innerText = `Spoilage Probability: ${percent}% (method: ${pred.method})`;

      appendLog(`Latest: T=${d.temperature}°C H=${d.humidity}% G=${d.gas} → ${pred.risk} (${percent}%)`);

      // voice alert if high risk
      if (percent >= 60) {
        speakAlert(`Warning: Spoilage probability is ${percent} percent. Take corrective action.`);
      }
    } else {
      appendLog("No data yet.");
    }
  } catch (e) {
    appendLog("Error fetching latest: " + e.message);
  }
}

function appendLog(text) {
  const p = document.createElement("p");
  p.innerText = `[${new Date().toLocaleTimeString()}] ${text}`;
  logEl.prepend(p);
  while (logEl.childElementCount > 50) logEl.removeChild(logEl.lastChild);
}

// Simple canvas chart drawing for temp/hum/gas
async function drawChart() {
  try {
    const res = await fetch(historyUrl);
    const payload = await res.json();
    if (payload.status !== "success") return;
    const data = payload.data.slice(-50); // last 50 readings

    const temps = data.map(r => Number(r.temperature));
    const hums = data.map(r => Number(r.humidity));
    const gases = data.map(r => Number(r.gas));
    const labels = data.map((r,i) => i+1);

    const canvas = document.getElementById("chart");
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0,0,canvas.width,canvas.height);

    const maxVal = Math.max(...temps, ...hums, ...gases, 1);
    const minVal = Math.min(...temps, ...hums, ...gases, 0);
    const margin = 40;
    const w = canvas.width - margin*2;
    const h = canvas.height - margin*2;

    function plotLine(values, dashOffset) {
      ctx.beginPath();
      for (let i=0;i<values.length;i++) {
        const x = margin + (i/(values.length-1 || 1)) * w;
        const y = margin + (1 - (values[i]-minVal)/(maxVal-minVal || 1)) * h;
        if (i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
      }
      ctx.lineWidth = 2;
      ctx.strokeStyle = "rgba(0,0,0,0.9)"; // darker for first line
      ctx.stroke();
    }

    // draw three overlapping lines (differing alpha)
    if (temps.length) plotLine(temps, 0);
    if (hums.length) plotLine(hums, 1);
    if (gases.length) plotLine(gases, 2);

    ctx.fillStyle = "#333";
    ctx.font = "12px Arial";
    ctx.fillText("Temp / Hum / Gas (raw)", 10, 14);

  } catch (e) {
    appendLog("Error drawing chart: " + e.message);
  }
}

// speak using Web Speech API (browser) — fallback: no-op
function speakAlert(text) {
  try {
    if ('speechSynthesis' in window) {
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'en-US';
      window.speechSynthesis.cancel(); // stop previous
      window.speechSynthesis.speak(utter);
    } else {
      console.log("Speech synthesis not supported.");
    }
  } catch (e) {
    console.log("Speech error:", e);
  }
}

// initial load
fetchLatest();
drawChart();

// refresh every 5 seconds
setInterval(() => {
  fetchLatest();
  drawChart();
}, 5000);
