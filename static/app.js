function formatDate(unixTs) {
  const date = new Date(unixTs * 1000);
  return date.toLocaleString('fi-FI');
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

  const details = document.getElementById('latestDetails');
  details.innerHTML = detailPairs
    .map(([key, value]) => `<div><dt>${key}</dt><dd>${value}</dd></div>`)
    .join('');
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

function drawTemperatureChart(rows) {
  const canvas = document.getElementById('temperatureChart');
  const ctx = canvas.getContext('2d');
  const width = canvas.width;
  const height = canvas.height;
  const padding = 36;

  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = '#fcfdff';
  ctx.fillRect(0, 0, width, height);

  if (!rows.length) {
    ctx.fillStyle = '#1b2430';
    ctx.font = '16px Arial';
    ctx.fillText('Ei dataa', padding, height / 2);
    return;
  }

  const values = rows.map(r => Number(r.temperature ?? 0));
  const min = Math.min(...values) - 0.5;
  const max = Math.max(...values) + 0.5;
  const range = max - min || 1;

  ctx.strokeStyle = '#d8e0eb';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, height - padding);
  ctx.lineTo(width - padding, height - padding);
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, height - padding);
  ctx.stroke();

  ctx.strokeStyle = '#2155cd';
  ctx.lineWidth = 3;
  ctx.beginPath();

  rows.forEach((row, index) => {
    const x = padding + (index / Math.max(rows.length - 1, 1)) * (width - padding * 2);
    const y = height - padding - ((Number(row.temperature ?? 0) - min) / range) * (height - padding * 2);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  ctx.fillStyle = '#5f6b7a';
  ctx.font = '12px Arial';
  ctx.fillText(`${max.toFixed(1)} °C`, 8, padding);
  ctx.fillText(`${min.toFixed(1)} °C`, 8, height - padding);
  ctx.fillText('Vanhempi', padding, height - 10);
  ctx.fillText('Uusin', width - 70, height - 10);
}

async function loadData() {
  const [latest, history] = await Promise.all([
    fetchJson('/api/latest'),
    fetchJson('/api/history')
  ]);

  updateLatest(latest);
  updateTable(history);
  drawTemperatureChart(history);
}

document.getElementById('refreshButton').addEventListener('click', () => {
  loadData().catch(err => alert(err.message));
});

loadData().catch(err => alert(err.message));
