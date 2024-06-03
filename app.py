from flask import Flask, render_template, request, jsonify
from algorithm import neat_algo

app = Flask(__name__)

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
    data = request.form.to_dict()
    
    # Parse boolean values correctly
    data['reset_on_extinction'] = data.get('reset_on_extinction') == 'on'
    data['enabled_default'] = data.get('enabled_default') == 'on'
    data['feed_forward'] = data.get('feed_forward') == 'on'
    
    # Run algorithm from form config data
    result =  neat_algo.run(data)
    
    return jsonify({'message': result})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
