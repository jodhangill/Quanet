let fitnessFunc = "";
let textWidths = [];
let outputCount = 0;
let caretIndex = -1;


function setDisplaySize() {
    // Set height of calculator display based on other elements
    const calcPad = document.getElementById('calcPad');
    const displayContainer = document.getElementById('displayContainer');
    const homeButton = document.getElementById('homeButton');

    displayContainer.style.height = `${window.innerHeight - calcPad.offsetHeight - homeButton.offsetHeight - 36}px`;
}

function handleClick(event) {

    const id = event.target.id

    const caret = document.getElementById('caret');

    // Track the current function text
    if (id == 'backspace') {
        fitnessFunc = fitnessFunc.substring(0, fitnessFunc.length - 1);
        caretIndex--;
    }
    else if (id == 'clear') {
        fitnessFunc = "";
        textWidths = [];
        outputCount = 0;
        caretIndex = 0;
    }
    else if (id == 'done') {
        window.location.href = '/configurator';
    }
    else {
        caretIndex++;
        fitnessFunc += event.target.innerText;
    }
    
    // Display fitness function
    const output = document.getElementById('output');
    output.innerText = fitnessFunc;

    // Adjust caret position
    const outputFrame = output.getBoundingClientRect();
    textWidths.push(outputFrame.right)
    caret.style.top = outputFrame.top - 90 + 'px';
    caret.style.left = textWidths.at(caretIndex) - 16 + 'px';
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
};
window.addEventListener('resize', function(event) {
    setDisplaySize();
}, true);
