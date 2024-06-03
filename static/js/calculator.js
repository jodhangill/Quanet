
function setDisplaySize() {
    // Set height of calculator display based on other elements
    const calcPad = document.getElementById('calcPad');
    const displayContainer = document.getElementById('displayContainer');
    const homeButton = document.getElementById('homeButton');

    displayContainer.style.height = `${window.innerHeight - calcPad.offsetHeight - homeButton.offsetHeight - 36}px`;
}

window.onload = function () {
    setDisplaySize();
};
window.addEventListener('resize', function(event) {
    setDisplaySize();
}, true);