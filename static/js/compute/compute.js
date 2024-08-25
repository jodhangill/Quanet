window.onbeforeunload = function(e) {
    return 'Terminate computation?';
};

let currentIndex = 0;

function updateCarousel() {
    const charts = document.getElementById('charts');
    const slides = document.querySelectorAll('.chart-slide');
    const totalSlides = slides.length;

    if (currentIndex >= totalSlides) {
        currentIndex = 0;
    } else if (currentIndex < 0) {
        currentIndex = totalSlides - 1;
    }
    let tickers = JSON.parse(localStorage.getItem('tickers'));
    document.getElementById('curTicker').innerText = tickers[currentIndex];
    const offset = -currentIndex * 100;
    charts.style.transform = `translateX(${offset}%)`;
}

function next() {
    currentIndex++;
    updateCarousel();
}

function prev() {
    currentIndex--;
    updateCarousel();
}

// Initialize carousel
updateCarousel();