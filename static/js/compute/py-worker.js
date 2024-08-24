//py-worker.js

const pyodideWorker = new Worker("static/js/compute/webworker.js");

const callbacks = {};

function updateProgressBar(progress) {
    let bar = document.getElementById('loadingProgress');
    if (progress == 100) {
        bar.style.transitionDuration = '7000ms';
        document.getElementById('loadingText').innerHTML = 'Finalizing...'
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
    let tickers = JSON.parse(localStorage.getItem('tickers'));
    let chartList = document.getElementById('charts');

    for (let i = 0; i < graphs.length; i++) {
        let graph = graphs[i]

        let dates = graph.dates;
        let equity = graph.equity;
        let id = graph.data_id;
        let prices = graph.prices;

        // Map point colors on graph to type of order (buy/sell/hold)
        let pointColors = graph.orderSequence.map(value => {
            if (value === 'buy') return 'rgba(0,255,0,1)';
            if (value === 'sell') return 'rgba(255,0,0,1)';
            return 'rgba(0,0,0,0)';
        });
        let pointRadius = graph.orderSequence.map(value => {
            return value === 'hold' ? 0 : 2 + (9/graph.orderSequence.length);
        });

        // Convert date strings to JavaScript Date objects
        const formattedDates = dates.map(date => new Date(date).toISOString().split('T')[0]);

        let charts = document.createElement('div')

        // Create the chart
        let priceChart = document.createElement('canvas')
        priceChart.id = `priceChart${id}`
        charts.appendChild(priceChart)
        new Chart(priceChart, {
            type: 'line',
            data: {
                labels: formattedDates,
                datasets: [{
                    label: 'Share Price',
                    data: prices,
                    borderColor: 'rgba(200,225,255,0.8)',
                    borderWidth: 1,
                    pointBorderColor: pointColors,
                    pointBackgroundColor: 'rgba(0,0,0,0)',
                    pointRadius: pointRadius,
                    pointBorderWidth: 1,
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
                            text: 'Share Price'
                        }
                    }
                }
            }
        });

        let equityChart = document.createElement('canvas')
        equityChart.id = `equityChart${id}`
        charts.appendChild(equityChart)
        new Chart(equityChart, {
            type: 'line',
            data: {
                labels: formattedDates,
                datasets: [{
                    label: 'Equity',
                    data: equity,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderColor: 'rgba(200,255,200,0.8)',
                    borderWidth: 3,
                    pointRadius: 0,
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
        chartList.appendChild(charts)
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