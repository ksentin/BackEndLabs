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

from flask_jwt_extended import create_access_token, JWTManager
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity


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


app.config["JWT_SECRET_KEY"] = "jose"
jwt = JWTManager(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )

@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )

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


@app.route('/currencies', methods=['GET'])
@jwt_required()
def get_currencies():
    currency_schema = CurrencySchema(many=True)
    return jsonify(currency_schema.dump(Currency.query.all())), 200

@app.route('/register', methods=['POST'])
def register_user():
    user_schema = UserSchema()
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    currency_name = data.get('default_currency_name')
    currency = Currency.query.filter_by(name=currency_name).first()

    if not currency:
        currency = Currency(name=currency_name)
        db.session.add(currency)
        db.session.commit()

    hashed_password = pbkdf2_sha256.hash(data['password'])

    user = User(name=data['name'], default_currency_id=currency.id, password=hashed_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "name": user.name,
        "default_currency": user.default_currency.name,
    }), 201


@app.route('/login', methods=['POST'])
def login_user():
    user_schema = UserSchema()
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    username = data.get('name')
    password = data.get('password')

    user = User.query.filter_by(name=username).first()

    if user and pbkdf2_sha256.verify(password, user.password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    user_schema = UserSchema(many=True)
    return jsonify(user_schema.dump(users)), 200


@app.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        user_schema = UserSchema()
        return jsonify(user_schema.dump(user)), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/user/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404


@app.route('/category', methods=['POST'])
@jwt_required()
def create_category():
    data = request.get_json()

    errors = CategorySchema().validate(data)
    if errors:
        return jsonify({"error": errors}), 400

    is_custom = data.get('is_custom', False)
    user_id = data.get('user_id', 0)

    if is_custom:
        user_exists = User.query.filter_by(id=user_id).first()
        if not user_exists:
            return jsonify({"error": "User with specified user_id not found"}), 404

    category = Category(name=data['name'], is_custom=is_custom, user_id=user_id)

    db.session.add(category)
    db.session.commit()

    return jsonify({"id": category.id, "name": category.name, "is_custom": category.is_custom, "user_id": category.user_id}), 201


@app.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = Category.query.all()
    category_schema = CategorySchema(many=True)
    return jsonify(category_schema.dump(categories)), 200


@app.route('/category/<category_id>', methods=['DELETE'])
@jwt_required()
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
@jwt_required()
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

    if category.is_custom and category.user_id != user_id:
        return jsonify({"error": "Wrong user to use this category"}), 403

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
@jwt_required()
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

    records_data = []
    for record in records:
        user_name = User.query.get(record.user_id).name
        category_name = Category.query.get(record.category_id).name
        currency_name = record.currency.name if record.currency else None

        record_data = {
            "id": record.id,
            "user": user_name,
            "category": category_name,
            "amount": record.amount,
            "currency": currency_name,
            "created_at": record.created_at
        }
        records_data.append(record_data)

    return jsonify(records_data), 200


@app.route('/record/<record_id>', methods=['GET'])
@jwt_required()
def get_record(record_id):
    record = Record.query.get(record_id)
    if record:
        record_schema = RecordSchema()
        return jsonify(record_schema.dump(record)), 200
    else:
        return jsonify({"message": "Record not found"}), 404


@app.route('/record/<record_id>', methods=['DELETE'])
@jwt_required()
def delete_record(record_id):
    record = Record.query.get(record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully"}), 200
    else:
        return jsonify({"message": "Record not found"}), 404