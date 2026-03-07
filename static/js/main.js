
// Toggle visibility for graphs and table
document.addEventListener('DOMContentLoaded', function() {
	const graphsSection = document.getElementById('graphs-section');
	const tableSection = document.getElementById('table-section');
	const btnGraphs = document.getElementById('toggle-graphs');
	const btnTable = document.getElementById('toggle-table');

	btnGraphs.addEventListener('click', function() {
		if (graphsSection.style.display === 'none') {
			graphsSection.style.display = '';
		} else {
			graphsSection.style.display = 'none';
		}
	});

	btnTable.addEventListener('click', function() {
		if (tableSection.style.display === 'none') {
			tableSection.style.display = '';
		} else {
			tableSection.style.display = 'none';
		}
	});
});

async function loadData() {
	const res = await fetch('/api/readings?limit=60');
	return await res.json();
}
(async () => {
	const data = await loadData();
	const labels = data.map(x => x.time);
	const temps = data.map(x => x.tempc);
	const hums = data.map(x => x.humidity);
	new Chart(document.getElementById('tempChart').getContext('2d'), {
		type: 'line',
		data: { labels, datasets: [{ label: 'Temp (C)', data: temps, tension: 0.2 }] },
		options: { responsive: true, scales: { x: { display: false } } }
	});
	new Chart(document.getElementById('humChart').getContext('2d'), {
		type: 'line',
		data: { labels, datasets: [{ label: 'Humidity (%)', data: hums, tension: 0.2 }] },
		options: { responsive: true, scales: { x: { display: false } } }
	});
})();
