let graph_data = document.getElementById("points_case_duration_graph").value;
console.log(graph_data)
new Chart(document.getElementById("line-chart"), {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Scatter Dataset',
            data: graph_data,
            backgroundColor: 'rgb(255, 99, 132)'
        }],
    },
    options: {
        title: {
            display: true,
            text: 'World population per region (in millions)'
        }
    }
});