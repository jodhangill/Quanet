function updateProgressBar(progress) {
    document.getElementById('bar').style.width = progress + '%';
}

// Get current route
var currentRoute = window.location.pathname;

// Update progress bar based on the current route
if (currentRoute === '/') {
    document.getElementById('progress').style.display = 'none';
} else if (currentRoute === '/fitness'){
    document.getElementById('progress').style.display = 'flex';
    updateProgressBar(33);
} else if (currentRoute === '/configurator'){
    document.getElementById('progress').style.display = 'flex';
    updateProgressBar(66);
} else if (currentRoute === '/compute'){
    document.getElementById('progress').style.display = 'flex';
    updateProgressBar(100);
}
