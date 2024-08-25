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
        document.getElementById('loadingText').innerHTML = 'Running...'
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

function plotGraphs(graphs) {
    document.getElementById('chartControls').style.display = 'flex'
    let charts = document.getElementById('charts');
    while (charts.firstChild) {
        charts.removeChild(charts.firstChild);
    }

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

        let slide = document.createElement('div')
        slide.classList.add('chart-slide')
        slide.style.width = '100%';
        slide.style.flexShrink = 0;

        // Create the chart
        let combinedChart = document.createElement('canvas')
        combinedChart.id = `combinedChart${id}`
        combinedChart.style.display = 'block'
        combinedChart.style.width = '100%'
        combinedChart.style.height = 'auto'

        slide.appendChild(combinedChart)
        new Chart(combinedChart, {
            type: 'line',
            data: {
                labels: formattedDates,
                datasets: [
                    {
                        label: 'Share Price',
                        data: prices,
                        borderColor: 'rgba(200,225,255,0.8)',
                        borderWidth: 1,
                        pointBorderColor: pointColors,
                        pointBackgroundColor: 'rgba(0,0,0,0)',
                        pointRadius: pointRadius,
                        pointBorderWidth: 1,
                        yAxisID: 'y1', // ID for Share Price y-axis
                    },
                    {
                        label: 'Equity',
                        data: equity,
                        backgroundColor: 'rgba(0,0,0,0)',
                        borderColor: 'rgba(200,255,200,0.8)',
                        borderWidth: 3,
                        pointRadius: 0,
                        yAxisID: 'y2', // ID for Equity y-axis
                    }
                ]
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
                    y1: {
                        title: {
                            display: true,
                            text: 'Share Price'
                        },
                        position: 'left',
                        // Optionally adjust the range and step size
                        // min: 0,
                        // max: 100,
                        // stepSize: 10
                    },
                    y2: {
                        title: {
                            display: true,
                            text: 'Equity'
                        },
                        position: 'right',
                        // Optionally adjust the range and step size
                        // min: 0,
                        // max: 10000,
                        // stepSize: 500
                    }
                }
            }
        });

        charts.appendChild(slide)
    }
}

var screenData = [];
var displayedGen = 0
var totalGen = 0;

function displayGen(fade=null) {
    if (displayedGen >= totalGen) {
        displayedGen = 0;
    } else if (displayedGen < 0) {
        displayedGen = totalGen - 1;
    }
    if (totalGen > 0) {
        if (totalGen > 1) {
            document.getElementById('genControls').style.display = 'flex';
        }
        
        var data = screenData[displayedGen];
        var genome = data.genome;
        drawDot(genome.dot);
        plotGraphs(genome.graphs)

        let genOut = document.getElementById('genOutput');
        genOut.innerText = `Generation ${data.gen + 1}`
    }

    var compute = document.getElementById('computeContainer');
    compute.classList.remove("fade-left");
    compute.classList.remove("fade-right");
    compute.classList.remove("fade-up");
    if (fade == 'left') {
        compute.offsetHeight;
        compute.classList.add('fade-left');
    } else if (fade == 'right') {
        compute.offsetHeight;
        compute.classList.add('fade-right');
    } else {
        compute.offsetHeight;
        compute.classList.add('fade-up');
    }

}

function nextGen() {
    displayedGen++;
    displayGen('right');
}

function prevGen() {
    displayedGen--;
    displayGen('left');
}

var totalEvaled = 0;
var currentGen = 0;

pyodideWorker.onmessage = (event) => {
    let data = event.data
    if (typeof data === 'string') {
        data = JSON.parse(data)
    }

    const {log, update, genome, results, loading, error} = data
    let logOutput = document.getElementById("log")
    if (loading) {
        updateProgressBar(loading)
    }
    if (update) {
        let bar = document.getElementById('loadingProgress');
        bar.style.transitionDuration = '200ms';
        bar.style.width = 100*update.genome/update.total + '%';
        if (update.genome == update.total && update.total > 0) {
            totalGen++;
            console.log(totalGen)
        }
        if (update.gen >= 0) {
            currentGen = update.gen;
            console.log(currentGen)
        }
        if (update.total > 0) {
            totalEvaled = update.total
        }
        document.getElementById('loadingText').innerHTML = `Running generation ${currentGen + 1} (${update.genome}/${totalEvaled})`;

    }
    if (error) {
        console.log(error)
        logOutput.innerText += '\n' + error + '\n'
    }
    if (log) {
        console.log(log)
        logOutput.innerText += '\n' + log + '\n'
    }
    if (results) {
        console.log(results)
        logOutput.innerText += '\n' + results + '\n'        
    }
    if (genome) {
        console.log(genome);
        document.getElementById('genomeDisplay').style.display = 'block';
        screenData.push({
            'gen': currentGen,
            'genome': genome,
        })
        if (screenData.length >= 1) {
            displayGen()
        }
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

export { asyncRun, nextGen, prevGen };