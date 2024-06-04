let fitnessFunc = "";
let textWidths = [];


function setDisplaySize() {
    // Set height of calculator display based on other elements
    const calcPad = document.getElementById('calcPad');
    const displayContainer = document.getElementById('displayContainer');
    const homeButton = document.getElementById('homeButton');

    displayContainer.style.height = `${window.innerHeight - calcPad.offsetHeight - homeButton.offsetHeight - 36}px`;
}

function handleClick(event) {
    const id = event.target.id

    // Track the current function text
    if (id == 'backspace') {
        fitnessFunc = fitnessFunc.substring(0, fitnessFunc.length - 1);
    }
    else if (id == 'clear') {
        fitnessFunc = "";
    }
    else if (id == 'done') {
        window.location.href = '/configurator';
    }
    else {
        fitnessFunc += event.target.innerText;
    }

    // Display fitness function
    const output = document.getElementById('output');
    output.innerText = fitnessFunc;

    // Adjust caret position
    const outputFrame = output.getBoundingClientRect();
    const caret = document.getElementById('caret');
    caret.style.top = outputFrame.top - 90 + 'px';
    caret.style.left = outputFrame.right - 16 + 'px';
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
