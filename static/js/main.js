
// Toggle visibility for graphs and table
document.addEventListener('DOMContentLoaded', function() {
	const humChart = document.getElementById('humChart');
	const tempChart = document.getElementById('tempChart');
	const batteryChart = document.getElementById('batteryChart');
	const dataTable = document.getElementById('table-section');
	const btnHums = document.getElementById('toggle-hums');
	const btnTemp = document.getElementById('toggle-temp');
	const btnBattery = document.getElementById('toggle-battery');

	btnHums.addEventListener('click', function() {
		if (humChart.style.display === 'none') {
			humChart.style.display = '';
		} else {
			humChart.style.display = 'none';
			humChart.value = "Näytä ilmankosteus"
		}
	});

});

/* Call Flask API to get data */
/* Adjust ?limit=X to adjust how much data it gets (i.e. ?limit=420) */
async function loadData() {
	const res = await fetch('/api/readings?limit=60');
	return await res.json();
}

/* Create Chart.js charts and draw them onto id:s tempChart and humChart */
/* See documentation here: https://www.chartjs.org/docs/latest/ */
(async () => {
	// Fetch measurement data from the API
	const data = await loadData();

	// Extract time labels for the x-axis
	const labels = data.map(x => x.time);
	// Extract temperature values for the temperature chart
	const temps = data.map(x => x.tempc);
	// Extract humidity values for the humidity chart
	const hums = data.map(x => x.humidity);
	// Extract battery voltage values for battery capacity chart
	const battery = data.map(x => x.battery);

	// Create the temperature line chart
	new Chart(
		document.getElementById('tempChart').getContext('2d'), // Target canvas context
		{
			type: 'line', // Line chart
			data: {
				labels, // X-axis labels (timestamps)
				datasets: [{
					label: 'Temp (C)', // Legend label
					data: temps, // Y-axis data (temperatures)
					tension: 0.2 // Smooth the line
				}]
			},
			options: {
				responsive: true, // Make chart responsive
				scales: {
					x: { display: false } // Hide x-axis labels
				}
			}
		}
	);

	// Create the humidity line chart
	new Chart(
		document.getElementById('humChart').getContext('2d'), // Target canvas context
		{
			type: 'line', // Line chart
			data: {
				labels, // X-axis labels (timestamps)
				datasets: [{
					label: 'Humidity (%)', // Legend label
					data: hums, // Y-axis data (humidity)
					tension: 0.2 // Smooth the line
				}]
			},
			options: {
				responsive: true, // Make chart responsive
				scales: {
					x: { display: false } // Hide x-axis labels
				}
			}
		}
	);
	new Chart(
		document.getElementById('batteryChart').getContext('2d'), // Target canvas context
		{
			type: 'line', // Line chart
			data: {
				labels, // X-axis labels (timestamps)
				datasets: [{
					label: 'Battery (mV)', // Legend label
					data: battery, // Y-axis data (humidity)
					tension: 0.2 // Smooth the line
				}]
			},
			options: {
				responsive: true, // Make chart responsive
				scales: {
					x: { display: false } // Hide x-axis labels
				}
			}
		}
	);



})();
