from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    is_custom = fields.Boolean()
    user_id = fields.Integer()