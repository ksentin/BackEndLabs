from marshmallow import Schema, fields, validate

class RecordSchema(Schema):
    user_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    amount = fields.Float(required=True)
    currency_id = fields.Integer()