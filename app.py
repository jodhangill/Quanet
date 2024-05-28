from flask import Flask, render_template, request, jsonify
from algorithm import config_parser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Handle incoming message
@app.route('/process', methods=['POST'])
def process():
    data = request.form.to_dict()
    
    # Parse boolean values correctly
    data['reset_on_extinction'] = data.get('reset_on_extinction') == 'on'
    data['enabled_default'] = data.get('enabled_default') == 'on'
    data['feed_forward'] = data.get('feed_forward') == 'on'
    
    # Create config file and get the filename and message
    result =  config_parser.process_parameters(data)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
