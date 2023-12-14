from myapp import db
from sqlalchemy import func

class Currency(db.Model):
    __tablename__ = "currency"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(256), nullable=False)

    default_currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    default_currency = db.relationship('Currency', foreign_keys=[default_currency_id])

    records = db.relationship("Record", back_populates="user", lazy="dynamic")

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    is_custom = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, nullable=False, default=0)

    records = db.relationship("Record", back_populates="category", lazy="dynamic")

class Record(db.Model):
    __tablename__ = "record"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    user = db.relationship("User", back_populates="records")
    category = db.relationship("Category", back_populates="records", foreign_keys=[category_id])
    currency = db.relationship("Currency")