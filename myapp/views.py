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
    try:
        user_data = UserSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    user = User(id=str(uuid.uuid4()), **user_data)
    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "username": user.username})


@app.route('/users', methods=['GET'])
def get_users():
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users.values())), 200


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        user_schema = UserSchema()
        return jsonify(user_schema.dump(user)), 200
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

    errors = CategorySchema().validate(data)
    if errors:
        return jsonify({"error": errors}), 400

    category_id = str(uuid.uuid4())
    category = {"id": category_id, **data}
    categories[category_id] = category
    return jsonify(category), 201


@app.route('/categories', methods=['GET'])
def get_categories():
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(list(categories.values()))), 200


@app.route('/category/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    if not uuid.UUID(category_id, version=4):
        return jsonify({"error": "Invalid category_id format"}), 400

    category = categories.get(category_id)
    if category:
        del categories[category_id]
        category_schema = CategorySchema()
        return jsonify({"message": f"Category {category_id} has been deleted", "deleted_category": category_schema.dump(category)}), 200
    else:
        return jsonify({"message": "Category not found"}), 404


@app.route('/record', methods=['POST'])
def create_record():
    data = request.get_json()

    errors = RecordSchema().validate(data)
    if errors:
        return jsonify({"error": errors}), 400

    record_id = str(uuid.uuid4())

    record = {
        "id": record_id,
        "user_id": data['user_id'],
        "category_id": data['category_id'],
        "amount": data['amount'],
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    records[record_id] = record

    return jsonify(record), 201


@app.route('/records', methods=['GET'])
def get_records():
    user_id = request.args.get('user_id')
    category_id = request.args.get('category_id')

    errors = RecordSchema().validate({'user_id': user_id, 'category_id': category_id})
    if errors:
        return jsonify({"error": errors}), 400

    if not user_id and not category_id:
        return jsonify({"error": "Missing user_id and category_id parameters"}), 400

    filtered_records = []

    for record_id, record in records.items():
        if (not user_id or record['user_id'] == user_id) and (not category_id or record['category_id'] == category_id):
            filtered_records.append(record)

    record_schema = RecordSchema(many=True)
    return jsonify(record_schema.dump(filtered_records)), 200


@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    record = records.get(record_id)
    if record:
        record_schema = RecordSchema()
        return jsonify(record_schema.dump(record)), 200
    else:
        return jsonify({"message": "Record not found"}), 404


@app.route('/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    record = records.get(record_id)
    if record:
        del records[record_id]
        return jsonify({"message": "Record deleted successfully"}), 200
    else:
        return jsonify({"message": "Record not found"}), 404