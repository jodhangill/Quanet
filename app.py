import os
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from algorithm import neat_algo
import json

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
    # Retrieve parameters from session
    config = session.get('config')
    data_requests = session.get('data_requests')
    fitness_function = session.get('fitness_function')

    if not config or not data_requests or not fitness_function:
        return "Error: Missing data in session"

    return render_template('compute.html')




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
