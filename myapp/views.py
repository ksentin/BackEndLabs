from myapp import app
from flask import jsonify, request
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

from myapp.models import User, db, Category, Record, Currency

from schemes.user_schema import UserSchema
from schemes.сategory_schema import CategorySchema
from schemes.record_schema import RecordSchema
from schemes.currency_schema import CurrencySchema
from marshmallow import ValidationError

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


@app.route('/currency', methods=['POST'])
def create_currency():
    currency_schema = CurrencySchema()
    try:
        data = currency_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    currency = Currency(name=data['name'])
    db.session.add(currency)
    db.session.commit()

    return jsonify({"id": currency.id, "name": currency.name}), 201


@app.route('/currencies', methods=['GET'])
def get_currencies():
    currency_schema = CurrencySchema(many=True)
    return jsonify(currency_schema.dump(Currency.query.all())), 200



@app.route('/user', methods=['POST'])
def create_user():
    user_schema = UserSchema()
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    currency_id = data.get('default_currency_id')
    try:
        Currency.query.filter_by(id=currency_id).one()
    except NoResultFound:
        return jsonify({"error": f"Currency with id {currency_id} not found"}), 400

    user = User(name=data['name'], default_currency_id=currency_id)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "name": user.name,
        "default_currency": user.default_currency.name,
    }), 201


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users)), 200


@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        user_schema = UserSchema()
        return jsonify(user_schema.dump(user)), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/category', methods=['POST'])
def create_category():
    data = request.get_json()

    errors = CategorySchema().validate(data)
    if errors:
        return jsonify({"error": errors}), 400

    category = Category(name=data['name'])

    db.session.add(category)
    db.session.commit()

    return jsonify({"id": category.id, "name": category.name}), 201


@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories)), 200


@app.route('/category/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    if not uuid.UUID(category_id, version=4):
        return jsonify({"error": "Invalid category_id format"}), 400

    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        category_schema = CategorySchema()
        return jsonify({"message": f"Category {category_id} has been deleted", "deleted_category": category_schema.dump(category)}), 200
    else:
        return jsonify({"message": "Category not found"}), 404


@app.route('/record', methods=['POST'])
def create_record():
    data = request.get_json()

    try:
        RecordSchema().load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    user_id = int(data['user_id'])
    category_id = int(data['category_id'])
    amount = data['amount']

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with id {user_id} not found"}), 404

    category = Category.query.get(category_id)
    if not category:
        return jsonify({"error": f"Category with id {category_id} not found"}), 404

    currency_id = data.get('currency_id')
    if currency_id:
        try:
            currency = Currency.query.filter_by(id=currency_id).one()
        except NoResultFound:
            return jsonify({"error": f"Currency with id {currency_id} not found"}), 400
    else:
        currency = user.default_currency

    record = Record(
        user_id=user_id,
        category_id=category_id,
        amount=amount,
        currency=currency
    )

    db.session.add(record)
    db.session.commit()

    return jsonify({
        "id": record.id,
        "user": user.name,
        "category": category.name,
        "amount": record.amount,
        "currency": currency.name,
        "created_at": record.created_at
    }), 201


@app.route('/records', methods=['GET'])
def get_records():
    user_id = request.args.get('user_id')
    category_id = request.args.get('category_id')

    try:
        RecordSchema().validate({'user_id': user_id, 'category_id': category_id}, partial=True)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    if not user_id and not category_id:
        return jsonify({"error": "Missing user_id and category_id parameters"}), 400

    query = Record.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if category_id:
        query = query.filter_by(category_id=category_id)

    records = query.all()
    record_schema = RecordSchema(many=True)

    return jsonify(record_schema.dump(records)), 200


@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    record = Record.query.get(record_id)
    if record:
        record_schema = RecordSchema()
        return jsonify(record_schema.dump(record)), 200
    else:
        return jsonify({"message": "Record not found"}), 404


@app.route('/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    record = Record.query.get(record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully"}), 200
    else:
        return jsonify({"message": "Record not found"}), 404