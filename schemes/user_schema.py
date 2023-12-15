from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    default_currency_name = fields.String()
    password = fields.String(required=True)