//py-worker.js

const pyodideWorker = new Worker("static/js/compute/webworker.js");

const callbacks = {};

function updateProgressBar(progress) {
    let bar = document.getElementById('loadingProgress');
    if (progress == 100) {
        bar.style.transitionDuration = '5000ms';
    }
    else if (progress < 0) {
        document.getElementById('loadingContainer').style.display = 'none';
    }
    else {
        bar.style.transitionDuration = '1000ms';
    }
    bar.style.width = progress + '%';
}

function drawDot(dotString) {
    if (typeof Viz !== 'undefined') {
        try {
            // Initialize Viz.js
            const viz = new Viz();
            
            // Render the Dot string to SVG
            viz.renderSVGElement(dotString)
                .then(function(element) {
                    element.style.maxWidth = '100%'
                    const container = document.getElementById('net-container');
                    // Append the rendered SVG to the container
                    container.innerHTML = '';
                    container.appendChild(element);
                })
                .catch(error => {
                    console.error('Error rendering the graph:', error);
                });
        } catch (error) {
            console.error('Error initializing Viz.js:', error);
        }
    } else {
        console.error('Viz.js is not available.');
    }
}

function plot_graphs(graphs) {
    console.log(graphs)

    for (let i = 0; i < graphs.length; i++) {
        let graph = graphs[i]

        let dates = graph.dates;
        let equities = graph.equity;
        let id = graph.id;

        console.log(graph)

        // Convert date strings to JavaScript Date objects
        const formattedDates = dates.map(date => new Date(date).toISOString().split('T')[0]);
        // Create the chart
        let chart = document.createElement('canvas')
        chart.id = `equityChart${id}`

        document.getElementById('charts').appendChild(chart)

        const ctx = chart.getContext('2d');
        const equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: formattedDates,
                datasets: [{
                    label: 'Equity',
                    data: equities,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y;
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Equity'
                        }
                    }
                }
            }
        });        
    }

}

pyodideWorker.onmessage = (event) => {
    let data = event.data
    if (typeof data === 'string') {
        data = JSON.parse(data)
    }

    const {update, genome, results, loading, error} = data
    let log = document.getElementById("log")
    if (loading) {
        updateProgressBar(loading)
    }
    if (error) {
        console.log(error)
        log.innerText += '\n' + error + '\n'
    }
    if (update) {
        console.log(update)
        log.innerText += '\n' + update + '\n'
    }
    if (results) {
        console.log(results)
        log.innerText += '\n' + results + '\n'        
    }
    if (genome) {
        console.log(genome);
        drawDot(genome.dot);
        plot_graphs(genome.graphs);
    }
};

const asyncRun = (() => {
    let id = 0; // identify a Promise
    return (script, context) => {
        // the id could be generated more carefully
        id = (id + 1) % Number.MAX_SAFE_INTEGER;
        return new Promise((onSuccess) => {
            callbacks[id] = onSuccess;
            pyodideWorker.postMessage({
                ...context,
                python: script,
                id,
            });
        });
    };
})();

export { asyncRun };