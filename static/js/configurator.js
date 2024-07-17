function saveAll() {
    var form = document.getElementById('neatForm');
    localStorage.setItem('formHTML', form.innerHTML);
}

function removeData(event, button) {
    event.preventDefault();
    var element = button.closest('.ticker_data');
    element.parentNode.removeChild(element);
    var tickerList = document.getElementById('tickerList');
    var tickerList = document.getElementById('tickerList');
    var dataList = document.getElementsByClassName('ticker_data');
    if (dataList.length == 0) {
        tickerList.innerHTML += `            
            <div id="noTickerMessage" class="text-center w-full">
                <span>No Data Added</span>
            </div>`;
    }
    saveAll();
}

function addTickerData(event) {
    event.preventDefault();
    var ticker = document.getElementById('ticker')
    var start = document.getElementById('startDate')
    var end = document.getElementById('endDate')
    var interval = document.getElementById('interval')

    ticker.style.borderColor = '';
    interval.style.borderColor = '';
    start.style.borderColor = '';
    end.style.borderColor = '';

    var missing = false;
    if (!ticker.value) {
        ticker.style.borderColor = 'orange';
        missing = true;
    }
    if (!interval.value) {
        interval.style.borderColor = 'orange';
        missing = true;
    }
    if (!start.value) {
        start.style.borderColor = 'orange';
        missing = true;
    }
    if (!end.value) {
        end.style.borderColor = 'orange';
        missing = true;
    }
    if (missing) return;
    var tickerTemplate = `
            <div class="ticker_data flex justify-center my-5">
                <div class="ticker_data_container">
                    <div>
                        <span class='ticker'>${ticker.value}</span>
                    </div>
                    <div>
                        <span class='interval'>${interval.value}</span>
                    </div>
                    <div>
                        <span class='start' value=${start.value}>${start.value.substring(2)}</span>
                    </div>
                    <div class="col-start-3 md:col-start-4">
                        <span class='end' value=${end.value}>${end.value.substring(2)}</span>
                    </div>
                </div>  
                <button onclick="removeData(event, this)" type="button" class="x-button">✕</button>                
            </div>
        `
    var tickerList = document.getElementById('tickerList');
    var message = document.getElementById('noTickerMessage');
    if (message) {
        tickerList.removeChild(message);
    }
    tickerList.innerHTML += tickerTemplate
    ticker.value = '';
    start.value = '';
    end.value = '';
    ticker.style.borderColor = '';
    interval.style.borderColor = '';
    start.style.borderColor = '';
    end.style.borderColor = '';
    saveAll();
}

function jumpTo(id) {
    const element = document.getElementById(id);
    element.scrollIntoView();
    window.scrollBy(0, -100);
}

function openJumpTo() {
    const dropDown = document.getElementById('drop-down');
    dropDown.hidden = false;
}

function closeJumpTo() {
    const dropDown = document.getElementById('drop-down');
    dropDown.hidden = true;
}

function toggleJumpTo(event) {
    const dropDown = document.getElementById('drop-down');
    if (dropDown.hidden) {
        dropDown.hidden = false;
    }
    else {
        dropDown.hidden = true;
    }
}

async function loadData() {
    var formHTML = localStorage.getItem('formHTML');
    if (formHTML) {
        const list = document.getElementById('neatForm');
        list.innerHTML = formHTML;
    }

    var displayHTML = localStorage.getItem('displayHTML');
    if (displayHTML) {
        const fitness = document.getElementById('fitness');
        fitness.innerHTML = displayHTML;
    }
}

function submit(event) {
    event.preventDefault();
    var tickerDatas = document.getElementsByClassName('ticker_data');

    const result = Array.from(tickerDatas).map(div => {
        const ticker = div.querySelector('.ticker').innerText;
        const interval = div.querySelector('.interval').innerText;
        const start = div.querySelector('.start').getAttribute('value');
        const end = div.querySelector('.end').getAttribute('value');

        return {
            ticker,
            interval,
            start,
            end
        };
    });
    const datas = JSON.stringify(result);
    var fitness = localStorage.getItem('fitnessText');
    var formData = new FormData(this);
    formData.append("datas", datas);
    formData.append("fitness", fitness);
    fetch("/process-form", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById("output").innerText = "Response: " + data.message;
        })
        .catch(error => console.error('Error:', error));
};

// Save current input state to its HTML
function saveInput(event) {
    if (event) {
        var element = event.target;
        if (element.tagName == 'INPUT') {
            if (element.type == 'checkbox') {
                if (!element.checked) {
                    element.removeAttribute('checked')
                }
                else {
                    element.setAttribute('checked', true)
                }
            }
            else {
                element.setAttribute('value', element.value);
            }
        } 
    }
}

function setChangeListeners() {
    const inputElements = document.querySelectorAll('input, select');
    inputElements.forEach(input => {
        input.addEventListener('change', saveInput);
    })
}

window.onload = function () {
    document.getElementById("neatForm").addEventListener("submit", submit);
    loadData();
    setChangeListeners();
};


