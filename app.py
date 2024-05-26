from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Handle incoming message
@app.route('/process', methods=['POST'])
def process():
    message = request.form.get('message')
    print(message)

    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)
