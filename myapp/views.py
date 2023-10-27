import uuid

from myapp import app
from flask import jsonify, request
from datetime import datetime

users = {}
categories = {}

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


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = str(uuid.uuid4())
    user = {"id": user_id, **data}
    users[user_id] = user
    return jsonify(user)


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id in users:
        del users[user_id]
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/category', methods=['POST'])
def create_category():
    data = request.get_json()
    category_id = str(uuid.uuid4())
    category = {"id": category_id, **data}
    categories[category_id] = category
    return jsonify(category)


@app.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(list(categories.values()))



