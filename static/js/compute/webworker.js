// webworker.js

// Setup your project to serve `py-worker.js`. You should also serve
// `pyodide.js`, and all its associated `.asm.js`, `.json`,
// and `.wasm` files as well:
importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js");

async function loadPyodideAndPackages() {
    self.pyodide = await loadPyodide();
    await self.pyodide.loadPackage(["numpy", "pytz"]);
}
let pyodideReadyPromise = loadPyodideAndPackages();

self.onmessage = async (event) => {
    // make sure loading is done
    await pyodideReadyPromise;
    // Don't bother yet with this line, suppose our API is built in such a way:
    const { id, python, ...context } = event.data;
    // The worker copies the context in its own "memory" (an object mapping name to values)
    for (const key of Object.keys(context)) {
        self[key] = context[key];
    }
    // Now is the easy part, the one that is similar to working in the main thread:
    try {
        // Install packages and update loading bar
        self.postMessage({loading: 10});
        await self.pyodide.loadPackagesFromImports(python);
        self.postMessage({loading: 20});
        await self.pyodide.loadPackage("micropip");
        self.postMessage({loading: 30});
        micropip = pyodide.pyimport("micropip");
        self.postMessage({loading: 40});
        await micropip.install('neat-python');
        self.postMessage({loading: 50});
        await micropip.install('backtrader');
        self.postMessage({loading: 60});
        await micropip.install('pandas'); 
        self.postMessage({loading: 70});
        await micropip.install('numpy');
        self.postMessage({loading: 80});
        await micropip.install('graphviz');
        self.postMessage({loading: 95});
        self.postMessage({loading: 100});

        let results = await self.pyodide.runPythonAsync(python);
        self.postMessage({ results, id });
    } catch (error) {
        self.postMessage({ error: error.message, id });
    }
};