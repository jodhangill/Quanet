var tickerTemplate = `
<div class="ticker_data flex justify-center px-2 my-5">
    <div class="bg-gray-800 w-full py-2 px-4 teal-800 border-gray-500 border border-r-0 rounded rounded-r-none flex justify-between md:text-xl">
        <div>
            <span class="self-start"></span>
        </div>
        <div>
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>  
    <button onclick="removeData(event, this)" class="bg-gray-800 border-gray-500 rounded-l-none">✕</button>                
</div>
`

function removeData(event, button) {
    event.preventDefault();
    var element = button.closest('.ticker_data');
    element.parentNode.removeChild(element);
    var tickerList = document.getElementById('ticker_list');
    var dataList = document.getElementsByClassName('ticker_data');
    if (dataList.length == 0) {
        tickerList.innerHTML += `            
            <div id="no_ticker_message" class="text-center w-full">
                <span>No Data Added</span>
            </div>`;
    }
}

function addTickerData(event) {
    event.preventDefault();
    var ticker = document.getElementById('ticker')
    var start = document.getElementById('start_date')
    var end = document.getElementById('end_date')
    var interval = document.getElementById('interval')
    console.log(interval)
    var tickerTemplate = `
            <div class="ticker_data flex justify-center my-5">
                <div class="grid grid-cols-3 md:grid-cols-4 bg-gray-800 w-full py-2 px-2 border-gray-500 border border-r-0 rounded rounded-r-none md:text-xl">
                    <div>
                        <span class="self-start">${ticker.value}</span>
                    </div>
                    <div>
                        <span>${interval.value}</span>
                    </div>
                    <div>
                        <span value=${start.value}>${start.value.substring(2)}</span>
                    </div>
                    <div class="col-start-3 md:col-start-4">
                        <span value=${end.value}>${end.value.substring(2)}</span>
                    </div>
                </div>  
                <button onclick="removeData(event, this)" class="w-12 bg-gray-800 border-gray-500 rounded-l-none">✕</button>                
            </div>
        `
    var tickerList = document.getElementById('ticker_list');
    var message = document.getElementById('no_ticker_message');
    if (message) {
        tickerList.removeChild(message);
    }
    tickerList.innerHTML += tickerTemplate
    ticker.value = '';
    start.value = '';
    end.value = '';
}