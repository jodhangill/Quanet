let lastFocusOffset = 0;

function setDisplaySize() {
    // Set the height of the calculator display based on other elements
    const calcPad = document.getElementById('calcPad');
    const displayContainer = document.getElementById('displayContainer');
    const homeButton = document.getElementById('homeButton');

    displayContainer.style.height = `${window.innerHeight - calcPad.offsetHeight - homeButton.offsetHeight - 36}px`;
}

function setCaretToDefault() {
    // Set caret position to the default starting position
    const caret = document.getElementById('caret');
    caret.style.top = '28.5px';
    caret.style.left = '26px';
}

function updateWidths(textWidths, index) {
    // Update the widths of the text elements
    let widthToRemove = textWidths[index];
    while (index < textWidths.length - 1) {
        textWidths[index] = textWidths[index + 1] - widthToRemove;
        index++;
    }
    textWidths.pop();
}

function getCaretX(caretIndex) {
    // Calculate the x-position of the caret
    let xPos = 0;
    for (let i = 0; i <= caretIndex; i++) {
        xPos += outputDisplayData[i][1];
    }
    return xPos;
}

function updateOutputText() {
    // Update the output text display
    let outputStr = outputDisplayData.map(data => data[0]).join('');
    const output = document.getElementById('output');
    output.innerHTML += outputStr;
}

function backspace() {
    // Simulate backspace key press
    document.execCommand("delete", false, null);
}

function moveLeft() {
    // Move the caret left
    if (caretIndex > 0) {
        caretIndex--;
    }
}

function moveRight() {
    // Move the caret right
    if (caretIndex < outputDisplayData.length - 1) {
        caretIndex++;
    }
}

function clearDisplay() {
    // Clear the entire display
    const display = document.getElementById("display");
    const size = display.innerHTML.length;
    for (let i = 0; i < size; i++) {
        document.execCommand("delete", false, null);
    }
}

function addText(text) {
    // Add text to the display at the current caret position
    const display = document.getElementById('display');
    let selection, range;

    if (window.getSelection) {
        // Modern browsers
        display.focus();
        selection = window.getSelection();
        let startPos = Math.min(selection.anchorOffset, selection.focusOffset);
        let endPos = Math.max(selection.anchorOffset, selection.focusOffset);
        display.innerText = display.innerText.substring(0, startPos) + text + display.innerText.substring(endPos);
        selection.collapse(display.firstChild, startPos + text.length);
    } else if (selection = document.selection) {
        // IE <= 8
        if (selection.type !== "Control") {
            range = selection.createRange();
            range.move("character", text.length);
            range.select();
        }
    }
}

function isMobileDevice() {
    // Check if the device is a mobile device
    let check = false;
    (function (a) {
        if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true;
    })(navigator.userAgent || navigator.vendor || window.opera);
    return check;
}

function moveCaret(charCount) {
    // Move the caret by a specified number of characters
    let selection, range;
    if (window.getSelection) {
        selection = window.getSelection();
        if (selection.rangeCount > 0) {
            let textNode = selection.focusNode;
            let newOffset = Math.min(textNode.length, selection.focusOffset + charCount);
            if (newOffset < 0) {
                newOffset = 0;
            }
            selection.collapse(textNode, newOffset);
        }
    } else if (selection = document.selection) {
        if (selection.type !== "Control") {
            range = selection.createRange();
            range.move("character", charCount);
            range.select();
        }
    }
}

function setCaretPosition(caretPos) {
    // Set the caret to a specific position
    let difference = caretPos - window.getSelection().focusOffset;
    moveCaret(difference);
}

function handleClick(event) {
    // Handle button clicks
    const display = document.getElementById('display');
    display.contentEditable = true;
    display.focus();
    setCaretPosition(lastFocusOffset);

    const id = event.target.id;

    if (id === 'backspace') {
        backspace();
    } else if (id === 'left') {
        moveCaret(-1);
    } else if (id === 'right') {
        moveCaret(1);
    } else if (id === 'clear') {
        clearDisplay();
    } else if (id === 'done') {
        window.location.href = '/configurator';
    } else {
        addText(event.target.innerText);
    }

    // Update caret position
    const caret = document.getElementById('caret');
    const range = window.getSelection().getRangeAt(0).getClientRects()[0];
    if (range) {
        caret.style.left = `${range.right}px`;
        caret.style.top = `${range.top - 72}px`;
    } else {
        setCaretToDefault();
    }
    lastFocusOffset = window.getSelection().focusOffset;

    display.contentEditable = false;
}

function setClickHandlers() {
    // Set click handlers for all calculator buttons
    const buttonContainer = document.getElementById('calcPad');
    const buttons = buttonContainer.getElementsByTagName('button');

    for (let button of buttons) {
        button.onclick = handleClick;
    }
}

// Set up event listeners
window.onload = function () {
    setDisplaySize();
    setCaretToDefault();
    setClickHandlers();
};

window.addEventListener('resize', setDisplaySize, true);
