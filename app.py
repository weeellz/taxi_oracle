from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from serve import get_model_api

app = Flask(__name__)
CORS(app)
model_api = get_model_api()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

@app.route('/api', methods=['POST'])
def api():
    input_data = request.json
    output_data = model_api(input_data)
    response = jsonify({"result": float(output_data)})
    return response

if __name__ == "__main__":
    app.run(debug=True)