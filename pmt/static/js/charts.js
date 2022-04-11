const CHART = document.getElementById("case_distribution_chart");
console.log(CHART);
const labels = Utils.months({count: 7});
let lineChart = new Chart(CHART, {
    type: "line",
    labels: labels,
    datasets: [{
        label: 'My First Dataset',
        data: [65, 59, 80, 81, 56, 55, 40],
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }]
});