import uuid

from myapp import app
from flask import jsonify, request
from datetime import datetime

users = {}
categories = {}
records = {}

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


@app.route('/category/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = categories.get(category_id)
    if category:
        del categories[category_id]
        return jsonify({"message": f"Category {category_id} has been deleted"})
    else:
        return jsonify({"message": "Category not found"}), 404


@app.route('/record', methods=['POST'])
def create_record():
    data = request.get_json()
    record_id = str(uuid.uuid4())
    record = {"id": record_id, **data}
    records[record_id] = record
    return jsonify(record)


@app.route('/records', methods=['GET'])
def get_all_records():
    return jsonify(list(records.values()))


@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    record = records.get(record_id)
    if record:
        return jsonify(record)
    else:
        return jsonify({"message": "Record not found"}), 404