from marshmallow import Schema, fields

class CurrencySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)