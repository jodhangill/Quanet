const pyodideWorker = new Worker("static/js/compute/webworker.js");

const callbacks = {};

pyodideWorker.onmessage = (event) => {
    let data = event.data
    if (typeof data === 'string') {
        data = JSON.parse(data)
    }

    const {update, genome, results, error} = data
    let log = document.getElementById("log")
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