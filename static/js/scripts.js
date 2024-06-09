function updateProgressBar(progress) {
    document.getElementById('bar').style.width = progress + '%';
}

// Get current route
var currentRoute = window.location.pathname;

// Update progress bar based on the current route
if (currentRoute === '/') {
    document.getElementById('progress').style.display = 'none';
} else if (currentRoute === '/fitness'){
    updateProgressBar(33);
} else if (currentRoute === '/configurator'){
    updateProgressBar(66);
}     

