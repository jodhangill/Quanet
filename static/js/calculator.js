let outputDisplayData = [["", null]]; // [text:string, width:float]
let caretIndex = 0;
let lastWidth = 0;


function setDisplaySize() {
    // Set height of calculator display based on other elements
    const calcPad = document.getElementById('calcPad');
    const displayContainer = document.getElementById('displayContainer');
    const homeButton = document.getElementById('homeButton');

    displayContainer.style.height = `${window.innerHeight - calcPad.offsetHeight - homeButton.offsetHeight - 36}px`;
}

function updateWidths(textWidths, i) {
    let widthToRemove = textWidths[i];
    while (i < textWidths.length - 1) {
        textWidths[i] = textWidths[i + 1] - widthToRemove;
        i++;
    }
    textWidths.pop();
}

function getCaretX(caretInd) {
    let xPos = 0;
    for (let i = 0; i < caretInd + 1; i++) {
        xPos += outputDisplayData[i][1]
    }
    return xPos;
}

function updateOutputText() {
    let outputStr = "";
    for (let i = 0; i < outputDisplayData.length; i++) {
        outputStr = outputStr + outputDisplayData[i][0];
    }
    // Update display output element
    let output = document.getElementById('output');
    output.innerText = outputStr;
}

function backspace() {
    if (caretIndex > 0) {
        outputDisplayData.splice(caretIndex, 1);
        updateOutputText();
        caretIndex--;
        let output = document.getElementById('output');
        let outputFrame = output.getBoundingClientRect();
        lastWidth = outputFrame.right;        
    }
}

function moveLeft() {
    if (caretIndex > 0) {
        caretIndex--;
    }
}

function moveRight() {
    if (caretIndex < outputDisplayData.length - 1) {
        caretIndex++;
    }
}

function clear() {
    outputStr = "";
    lastWidth = outputDisplayData[0][1];
    outputDisplayData = [["", lastWidth]];
    caretIndex = 0;
    // Update display output element
    let output = document.getElementById('output');
    output.innerText = outputStr;
}

function addText(text) {
    // Update display text data
    caretIndex++;
    let data = [text, null]
    outputDisplayData.splice(caretIndex, 0, data);

    updateOutputText()

    // Update display width data
    let output = document.getElementById('output');
    let outputFrame = output.getBoundingClientRect();
    outputDisplayData[caretIndex][1] = outputFrame.right - lastWidth;
    lastWidth = outputFrame.right;
}

function handleClick(event) {
    const id = event.target.id

    const caret = document.getElementById('caret');

    // Track the current function text
    if (id == 'backspace') {
        backspace();
    }
    else if (id == 'left') {
        moveLeft();
    }
    else if (id == 'right') {
        moveRight();
    }
    else if (id == 'clear') {
        clear();
    }
    else if (id == 'done') {
        window.location.href = '/configurator';
    }
    else {
        addText(event.target.innerText);
    }

    // Adjust caret position
    const outputFrame = output.getBoundingClientRect();
    if (caretIndex != 0) {
        caret.style.top = outputFrame.top - 90 + 'px';
    }
    caret.style.left = getCaretX(caretIndex) - 16 + 'px';
}

function setClickHandlers() {
    const buttonContainer = document.getElementById('keyboard');

    // Get all calculator buttons
    const buttons = buttonContainer.getElementsByTagName('button');

        for (let i = 0; i < buttons.length; i++) {
        buttons[i].onclick = handleClick;
    }
}

window.onload = function () {
    setDisplaySize();
    setClickHandlers();
    const output = document.getElementById('output');
    const outputFrame = output.getBoundingClientRect();
    outputDisplayData[0][1] = lastWidth = outputFrame.right;
};
window.addEventListener('resize', function(event) {
    setDisplaySize();
}, true);
