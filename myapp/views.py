import uuid

from myapp import app
from flask import jsonify, request
from datetime import datetime

users = {}
categories = {}
records = {}

# 404 (Not Found)
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

# 400 (Bad Request)
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request"}), 400

# 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

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
        abort(404)


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id in users:
        del users[user_id]
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        abort(404)


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
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    amount = data.get('amount')

    if not user_id or not category_id or not amount:
        return jsonify({"error": "Missing required parameters"}), 400

    record_id = str(uuid.uuid4())

    record = {
        "id": record_id,
        "user_id": user_id,
        "category_id": category_id,
        "amount": amount,
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    records[record_id] = record

    return jsonify(record), 201


@app.route('/records', methods=['GET'])
def get_records():
    user_id = request.args.get('user_id')
    category_id = request.args.get('category_id')

    if not user_id and not category_id:
        return jsonify({"error": "Missing user_id and category_id parameters"}), 400

    filtered_records = []

    for record_id, record in records.items():
        if (not user_id or record['user_id'] == user_id) and (not category_id or record['category_id'] == category_id):
            filtered_records.append(record)

    return jsonify(filtered_records), 200


@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    record = records.get(record_id)
    if record:
        return jsonify(record)
    else:
        return jsonify({"message": "Record not found"}), 404


@app.route('/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    record = records.get(record_id)
    if record:
        del records[record_id]
        return jsonify({"message": "Record deleted successfully"})
    else:
        return jsonify({"message": "Record not found"}), 404