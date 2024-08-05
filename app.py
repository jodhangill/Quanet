import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
import os
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
import json
import pandas as pd
import zipfile
import io
import yfinance as yf

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

running_ips = {}
lock = threading.Lock()

def download_data(data_requests):
    datas = []
    for data_request in data_requests:
        data = yf.download(data_request.get('ticker'), start=data_request.get('start'), end=data_request.get('end'), interval=data_request.get('interval'))
        datas.append(data.to_csv())
    return datas

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fitness')
def fitness():
    return render_template('fitness-calculator.html')

@app.route('/configurator')
def configurator():
    return render_template('configurator.html')

# Handle incoming message
@app.route('/process-form', methods=['POST'])
def process_form():
    # Get the client's IP address
    client_ip = request.remote_addr
    print(client_ip)

    # Limit to one instance per IP
    with lock:
        if running_ips.get(client_ip, False):
            return jsonify({'message': 'Already running'}), 429
        running_ips[client_ip] = True

    try:
        config = request.form.to_dict()
        data_requests = json.loads(request.form['datas'])
        fitness_function = request.form['fitness']


        # Parse boolean values correctly
        config['reset_on_extinction'] = config.get('reset_on_extinction') == 'on'
        config['enabled_default'] = config.get('enabled_default') == 'on'
        config['feed_forward'] = config.get('feed_forward') == 'on'

        # Store parameters in session
        session['config'] = config
        session['data_requests'] = data_requests
        session['fitness_function'] = fitness_function

        # Pass parameters to compute route
        return redirect(url_for('compute'))
    finally:
        with lock:
            running_ips[client_ip] = False

@app.route('/compute')
def compute():
    return render_template('compute.html')

@app.route('/get-session-data', methods=['GET'])
def get_session_data():
    config = session.get('config')
    fitness_function = session.get('fitness_function')

    if not config or not fitness_function:
        return jsonify({'error': 'Missing data in session'}), 400

    return jsonify({
        'config': config,
        'fitness_function': fitness_function
    })

@app.route('/get-stock-data', methods=['GET'])
def get_stock_data():
    data_requests = session.get('data_requests')
    if not data_requests:
        return jsonify({'error': 'Missing data in session'}), 400
    
    stock_data = download_data(data_requests)

    # Create an in-memory ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for i, csv_data in enumerate(stock_data):
            filename = f"data{i+1}.csv"
            zip_file.writestr(filename, csv_data)

    zip_buffer.seek(0)
    # Send the ZIP file
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='data.zip')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
