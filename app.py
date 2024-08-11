import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, make_response
import json
import pandas as pd
import zipfile
import io
import yfinance as yf
import yfinance.shared as shared
from datetime import datetime, timedelta
import dateutil.relativedelta as rd

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fitness')
def fitness():
    return render_template('fitness-calculator.html')

@app.route('/configurator')
def configurator():
    return render_template('configurator.html')

def split_interval(interval):
    letters = ''
    numbers = ''
    for char in interval:
        if char.isalpha():
            letters += char
        elif char.isdigit():
            numbers += char
    return letters, numbers

def subtract_from_date(date_string, interval):
    date = datetime.strptime(date_string, '%Y-%m-%d')
    unit, quantity = split_interval(interval)
    print(quantity)

    # Subtract for at least 27 extra data points, accounting for an assumed a max of 3 consecutive days without any data
    if unit == 'd':
        return date - timedelta(days=(48*int(quantity)))
    elif unit == 'wk':
        return date - timedelta(weeks=(30*int(quantity)))
    elif unit == 'mo':
        return date - rd.relativedelta(months=(30*int(quantity)))
    elif unit == 'h':
        return date - timedelta(hours=(150*int(quantity)))
    elif unit == 'm':
        print(date - timedelta(minutes=(5000*int(quantity))))
        return date - timedelta(minutes=(5000*int(quantity)))
    else:
        print(unit)
        raise ValueError("Unsupported unit of time.")


def trim_data(df, reference_date_str, previous_rows=27):
    reference_date = pd.to_datetime(reference_date_str).tz_localize(df.index.tz)
    match_index = (df.index >= reference_date).argmax()
    start_index = max(0, match_index - previous_rows)

    filtered_df = df.iloc[start_index:]

    return filtered_df

def download_data(data_requests):
    data_files = []
    errors = []
    for data_request in data_requests:
        ticker = data_request.get('ticker')
        start = data_request.get('start')
        end = end=data_request.get('end')
        interval = data_request.get('interval')

        adjusted_start = subtract_from_date(start, interval)

        try:
            data = yf.download(ticker, start=adjusted_start, end=end, interval=interval)
        except Exception as e:
            errors.append(e)
        data_length = len(data) - 1

        if shared._ERRORS:
            print(next(iter(shared._ERRORS.values())))
            errors.append(next(iter(shared._ERRORS.values())))
        elif data_length < 28:
            print(data_length)
            errors.append(f"('${data_request.get('ticker')}: Only contains {data_length} data points. At least 28 data points required for initial computation')")

        trimmed_data = trim_data(data, start)
        file_name = ''.join(str(value) for value in data_request.values())
        print(file_name)
        trimmed_data.to_csv(file_name)

        data_files.append(file_name)
    print(data_files)
    return data_files, errors

# Handle form submission
@app.route('/process-form', methods=['POST'])
def process_form():

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
