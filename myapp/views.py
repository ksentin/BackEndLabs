from myapp import app
from flask import jsonify
from datetime import datetime

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = {
        'status': 'success',
        'message': 'Service is running',
        'current_time': current_time
    }
    return jsonify(response), 200

@app.route('/', methods=['GET'])
def home():
    return 'This is the main endpoint.', 200