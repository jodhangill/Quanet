let lastFocusOffset = 0;
let node = 0;
let displayCount = 0;

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

function backspace() {
    // Simulate backspace key press
    const display = document.getElementById('display');
    if (window.getSelection && display.childNodes.length !== 0) {
        const selection = window.getSelection();
        let startPos = Math.min(selection.anchorOffset, selection.focusOffset);
        let afterText = display.childNodes[node].textContent.substring(startPos);

        if (display.childNodes[node].textContent[startPos - 1] === "‎") {
            display.removeChild(display.childNodes[node].previousSibling);
            display.removeChild(display.childNodes[node - 1]);
            document.execCommand("delete", false, null);
            node -= 2;

            if (afterText.length !== 0) {
                addText(afterText);
                moveCaret(-afterText.length);
            }
        } else {
            document.execCommand("delete", false, null);
        }
        displayCount--;
    }
}

function clearDisplay() {
    // Clear the entire display
    for (let i = 0; i < displayCount; i++) {
        moveCaretRight();
    }
    let total = displayCount;
    for (let i = 0; i < total; i++) {
        backspace();
    }
}

function addText(text, isSpan = false, isStyled = false, color = '', size = '') {
    // Add text to the display at the current caret position
    const display = document.getElementById('display');
    let selection;
    const length = text.length;
    let span;

    if (isSpan) {
        span = document.createElement('span');
        span.textContent = text;
        if (isStyled) {
            span.style.cssText = `color: ${color}; font-size: ${parseInt(size, 10) * 3 / 4}px; border: 1px solid ${color}; border-radius: 4px; padding: 0 2px; margin: 0 4px; position: relative; top: ${(parseInt(size, 10) - 24) / 3}px;`;
        }
    }

    if (window.getSelection) {
        // Modern browsers
        display.focus();
        selection = window.getSelection();
        let startPos = Math.min(selection.anchorOffset, selection.focusOffset);
        let endPos = Math.max(selection.anchorOffset, selection.focusOffset);

        if (isSpan && display.childNodes.length === 0) {
            display.appendChild(document.createTextNode("‎"));
            display.appendChild(span);
            display.appendChild(document.createTextNode("‎"));
            node += 2;
            selection.collapse(display.childNodes[node], 1);
        } else if (isSpan) {
            let beforeText = display.childNodes[node].textContent.substring(0, startPos);
            let afterText = display.childNodes[node].textContent.substring(endPos);
            display.childNodes[node].textContent = beforeText + "‎";
            display.insertBefore(span, display.childNodes[node].nextSibling);
            display.insertBefore(document.createTextNode("‎"), span.nextSibling);
            span.nextSibling.textContent += afterText;
            node += 2;
            selection.collapse(display.childNodes[node], 1);
        } else if (display.childNodes.length === 0 || display.firstChild.tagName === 'SPAN') {
            display.insertBefore(document.createTextNode(text), display.firstChild);
            selection.collapse(display.firstChild, length);
        } else {
            display.childNodes[node].textContent = display.childNodes[node].textContent.substring(0, startPos) + text + display.childNodes[node].textContent.substring(endPos);
            selection.collapse(display.childNodes.item(node), startPos + length);
        }
        displayCount++;
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

function moveCaretLeft() {
    // Move the caret to the left
    const display = document.getElementById('display');
    let selection;
    if (window.getSelection && displayCount > 0) {
        selection = window.getSelection();
        if (display.childNodes[node].textContent[selection.focusOffset - 1] === "‎") {
            // Move past span element
            node -= 2;
            selection.collapse(display.childNodes[node], display.childNodes[node].textContent.length - 1);
        } else if (node !== 0 || selection.focusOffset !== 0) {
            selection.collapse(display.childNodes[node], selection.focusOffset - 1);
        }
    }
}

function moveCaretRight() {
    // Move the caret to the right
    const display = document.getElementById('display');
    let selection;
    if (window.getSelection && displayCount > 0) {
        selection = window.getSelection();
        if (display.childNodes[node].textContent[selection.focusOffset] === "‎") {
            // Move past span element
            node += 2;
            selection.collapse(display.childNodes[node], 1);
        } else if (node !== display.childNodes.length - 1 || selection.focusOffset !== display.childNodes[node].length) {
            selection.collapse(display.childNodes[node], selection.focusOffset + 1);
        }
    }
}

function moveCaret(charCount) {
    // Move the caret by a specified number of characters
    let selection;
    if (window.getSelection) {
        selection = window.getSelection();
        if (selection.rangeCount > 0) {
            let textNode = selection.focusNode;
            let newOffset = Math.min(textNode.length, selection.focusOffset + charCount);
            if (newOffset < 0) newOffset = 0;
            selection.collapse(textNode, newOffset);
        }
    }
}

function setCaretPosition(caretPos) {
    // Set the caret to a specific position
    const display = document.getElementById('display');
    const selection = window.getSelection();
    selection.collapse(display.childNodes[node], caretPos);
}

function handleClick(event) {
    // Handle button clicks
    const display = document.getElementById('display');
    const size = window.getComputedStyle(display).getPropertyValue('font-size');
    display.contentEditable = true;
    display.focus();
    setCaretPosition(lastFocusOffset);

    const id = event.target.id;

    switch (id) {
        case 'backspace':
            backspace();
            break;
        case 'left':
            moveCaretLeft();
            break;
        case 'right':
            moveCaretRight();
            break;
        case 'clear':
            clearDisplay();
            break;
        case 'done':
            window.location.href = '/configurator';
            break;
        default:
            if (event.target.classList.contains('metric')) {
                const color = window.getComputedStyle(event.target).getPropertyValue('color');
                addText(event.target.innerText, true, true, color, size);
            } else if (event.target.innerText.length > 1) {
                addText(event.target.innerText, true, false);
            } else {
                addText(event.target.innerText, false);
            }
    }

    // Update caret position
    const caret = document.getElementById('caret');
    const range = window.getSelection().getRangeAt(0).getClientRects()[0];
    if (range) {
        caret.style.left = `${range.right}px`;
        caret.style.top = `${range.top - 92 + parseInt(size, 10)}px`;
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
