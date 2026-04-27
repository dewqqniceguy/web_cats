import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.String, default="u")
    balance = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0.00)
    product = orm.relationship("Product", back_populates='user')
    comments = orm.relationship("Comment", back_populates="user")
    purchases_as_buyer = orm.relationship("Purchase", foreign_keys="Purchase.buyer_id", back_populates="buyer")
    purchases_as_seller = orm.relationship("Purchase", foreign_keys="Purchase.seller_id", back_populates="seller")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

