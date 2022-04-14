new Chart(document.getElementById("case_duration_graph"), {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Scatter Dataset',
            data: points_case_duration_graph,
            backgroundColor: 'rgb(255, 99, 132)',
        }],
    },
    options: {
        title: {
            display: true,
            text: 'Distribution of case duration'
        }
    }
});

new Chart(document.getElementById("events_over_time_graph"), {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Scatter Dataset',
            data: points_events_over_time_graph,
            backgroundColor: 'rgb(255, 99, 132)',

        }],
    },
    options: {
        title: {
            display: true,
            text: 'Distribution of events over time'
        }
    }
});