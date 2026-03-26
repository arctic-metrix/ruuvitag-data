function formatDate(val) {
  const date = typeof val === 'string' ? new Date(val.replace(' ', 'T')) : new Date(val * 1000);
  return isNaN(date) ? val : date.toLocaleString('fi-FI');
}

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Virhe haettaessa ${url}`);
  }
  return res.json();
}
 
function updateLatest(latest) {
  setText('temperatureValue', `${Number(latest.temperature ?? 0).toFixed(1)} °C`);
  setText('humidityValue', `${Number(latest.humidity ?? 0).toFixed(1)} %`);
  setText('pressureValue', `${Number(latest.pressure ?? 0).toFixed(1)} hPa`);
  setText('batteryValue', `${Number(latest.battery_voltage ?? 0).toFixed(2)} V`);

  const detailPairs = [
    ['MAC', latest.mac ?? '--'],
    ['Aikaleima', formatDate(latest.ts_unix)],
    ['Liikelaskuri', latest.movement_counter ?? '--'],
    ['Sekvenssi', latest.measurement_sequence_number ?? '--']
  ];
}

function updateTable(rows) {
  const tbody = document.getElementById('historyTableBody');
  tbody.innerHTML = rows
    .slice()
    .reverse()
    .map(row => `
      <tr>
        <td>${formatDate(row.ts_unix)}</td>
        <td>${row.mac ?? '--'}</td>
        <td>${Number(row.temperature ?? 0).toFixed(1)} °C</td>
        <td>${Number(row.humidity ?? 0).toFixed(1)} %</td>
        <td>${Number(row.pressure ?? 0).toFixed(1)} hPa</td>
        <td>${Number(row.battery_voltage ?? 0).toFixed(2)} V</td>
      </tr>
    `)
    .join('');
}

function drawChart(rows, canvasId, property, unit, color, offset) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;
  const padding = 50; 

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = '#fcfdff';
  ctx.fillRect(0, 0, width, height);

  if (!rows.length) {
    ctx.fillStyle = '#1b2430';
    ctx.font = '16px Arial';
    ctx.fillText('Ei dataa', padding, height / 2);
    return;
  }

  const values = rows.map(r => Number(r[property] ?? 0));
  const min = Math.min(...values) - offset;
  const max = Math.max(...values) + offset;
  const range = max - min || 1;

  ctx.strokeStyle = '#d8e0eb';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, height - padding);
  ctx.stroke();

  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.beginPath();

  rows.forEach((row, index) => {
    const x = padding + (index / Math.max(rows.length - 1, 1)) * (width - padding * 2);
    const y = height - padding - ((Number(row[property] ?? 0) - min) / range) * (height - padding * 2);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.fillStyle = '#5f6b7a';
  ctx.font = '12px Arial';
  const decimals = property === 'battery_voltage' ? 2 : 1;
  ctx.fillText(`${max.toFixed(decimals)} ${unit}`, 5, padding);
  ctx.fillText(`${min.toFixed(decimals)} ${unit}`, 5, height - padding);
  ctx.fillText('Vanhempi', padding, height - 10);
  ctx.fillText('Uusin', width - 70, height - 10);
}

function drawCharts(rows) {
  drawChart(rows, 'temperatureChart', 'temperature', '°C', '#2155cd', 0.5);
  drawChart(rows, 'humidityChart', 'humidity', '%', '#2ca02c', 1.0);
  drawChart(rows, 'pressureChart', 'pressure', 'hPa', '#d62728', 1.0);
  drawChart(rows, 'batteryChart', 'battery_voltage', 'mV', '#ff7f0e', 0.1);
}

async function loadData() {
  const [latest, history] = await Promise.all([
    fetchJson('/api/latest'),
    fetchJson('/api/history')
  ]);

  updateLatest(latest);
  updateTable(history);
  drawCharts(history);
}

function pollData() {
  // Stop running if the toggle was switched off
  if (live === 0) return; 
  
  loadData().catch(err => alert(err.message));
  
  // Schedule the next execution in 2000ms
  timeoutId = setTimeout(pollData, 2000);
}

document.getElementById('refreshButton').addEventListener('click', () => {
  if (live === 1) {
    live = 0;
    document.getElementById('refreshButton').innerHTML = "Aloita live-päivitys"
    clearTimeout(timeoutId); // Cancel any pending timeout immediately
  } else {
    live = 1;
    document.getElementById('refreshButton').innerHTML = "Lopeta live-päivitys"
    pollData(); // Start the polling cycle
  }
});

let live = 0;
let timeoutId;
loadData().catch(err => alert(err.message));
