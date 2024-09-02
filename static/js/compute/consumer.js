import { asyncRun, nextGen, prevGen} from "./py-worker.js";

window.nextGen = nextGen;
window.prevGen = prevGen;

async function fetchSessionData() {
    try {
        const response = await fetch('/get-session-data');
        const data = await response.json();
        
        if (response.ok) {
            return data;
        } else {
            return `Error: ${data.error}`;
        }
    } catch (error) {
        return `Error: ${error.message}`;
    }
}
        
async function fetchStockData() {
    try {
        const response = await fetch('/get-stock-data');
        const blob = await response.blob();
        if (response.ok) {
            const zip = new JSZip();
            const zipContent = await zip.loadAsync(blob);
            
            const csvContents = []; // List to store all CSV file contents
            
            // Iterate over the entries in the ZIP file
            const filePromises = [];
            zipContent.forEach((relativePath, file) => {
                filePromises.push(file.async('text').then(fileContent => {
                    csvContents.push(fileContent); // Store each file's content in the lis
                }));
            });
            
            await Promise.all(filePromises);
            return csvContents;
        } else {
            return [`Error: ${response.statusText}`];
        }
    } catch (error) {
        return [`Error: ${error.message}`];
    }
}

async function main() {

    const pyFile = await fetch('static/python/main.py')
    const script = await pyFile.text();

    const session_data = await fetchSessionData();
    const data = await fetchStockData();

    const context = {
        config: JSON.stringify(session_data.config),
        fit_func: session_data.fitness_function,
        data: data,
    };

    try {
        const { results, error } = await asyncRun(script, context);
        if (results) {
            console.log("pyodideWorker return results: ", results);
        } else if (error) {
            console.log("pyodideWorker error: ", error);
        }
    } catch (e) {
        console.log(
            `Error in pyodideWorker at ${e.filename}, Line: ${e.lineno}, ${e.message}`,
        );
    }
}
main();