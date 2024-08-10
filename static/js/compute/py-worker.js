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

pyodideWorker.onmessage = (event) => {
    let data = event.data
    if (typeof data === 'string') {
        data = JSON.parse(data)
    }

    const {update, genome, dot, results, loading, error} = data
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
        console.log(genome)
    }
    if (dot) {
        if (typeof Viz !== 'undefined') {
            try {
                // Initialize Viz.js
                const viz = new Viz();
                
                // Render the Dot string to SVG
                viz.renderSVGElement(dot)
                    .then(function(element) {
                        // Append the rendered SVG to the container
                        document.getElementById('graph-container').appendChild(element);
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