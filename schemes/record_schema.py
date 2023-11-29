from marshmallow import Schema, fields, validate

class RecordSchema(Schema):
    user_id = fields.UUID(required=True)
    category_id = fields.UUID(required=True)
    amount = fields.Float(required=True)