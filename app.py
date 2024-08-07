import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
import os
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, make_response
import json
import pandas as pd
import zipfile
import io
import yfinance as yf
import yfinance.shared as shared

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

running_ips = {}
lock = threading.Lock()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fitness')
def fitness():
    return render_template('fitness-calculator.html')

@app.route('/configurator')
def configurator():
    return render_template('configurator.html')

def download_data(data_requests):
    data_files = []
    errors = []
    for data_request in data_requests:
        try:
            data = yf.download(data_request.get('ticker'), start=data_request.get('start'), end=data_request.get('end'), interval=data_request.get('interval'))
        except Exception as e:
            errors.append(e)
        file_name = ''.join(str(value) for value in data_request.values())
        if shared._ERRORS:
            print(next(iter(shared._ERRORS.values())))
            errors.append(next(iter(shared._ERRORS.values())))
        print(file_name)
        data.to_csv(file_name)
        data_files.append(file_name)
    print(data_files)
    return data_files, errors

# Handle form submission
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

        data_files, errors = download_data(data_requests)

        if errors:
            for file in data_files:
                os.remove(file)
            response_errors = []
            for e in errors:
                parts = e.split("('")
                if len(parts) > 1:
                    extracted_string = parts[1].split("')")[0]
                    response_errors.append(extracted_string)
            return make_response({'errors': response_errors}, 404)
        if not data_files:
            return make_response({'errors': ['Please Add Ticker Data']}, 404)

        # Parse boolean values correctly
        config['reset_on_extinction'] = config.get('reset_on_extinction') == 'on'
        config['enabled_default'] = config.get('enabled_default') == 'on'
        config['feed_forward'] = config.get('feed_forward') == 'on'

        # Store parameters in session
        session['config'] = config
        session['data_files'] = data_files
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

def create_zip_file(file_list):
    # Create a BytesIO object to hold the zip file in memory
    zip_buffer = io.BytesIO()

    # Create a new zip file and write to the BytesIO buffer
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in file_list:
            # Add each file to the zip archive
            zipf.write(file, arcname=os.path.basename(file))
            os.remove(file)

    # Move to the beginning of the BytesIO buffer
    zip_buffer.seek(0)

    return zip_buffer

@app.route('/get-stock-data', methods=['GET'])
def get_stock_data():
    data_files = session.get('data_files')
    if not data_files:
        return jsonify({'error': 'Missing data in session'}), 400

    # Create zip file in memory
    zip_buffer = create_zip_file(data_files)

    # Send the ZIP file
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='data.zip')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
