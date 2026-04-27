import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from datetime import datetime


class Purchase(SqlAlchemyBase):
    __tablename__ = 'purchases'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    buyer_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    seller_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    product_title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    product_price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    amount_paid = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # сколько заплатил покупатель
    seller_received = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # сколько получил продавец (90%)
    admin_received = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # сколько получил админ (10%)
    purchase_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    buyer = orm.relationship("User", foreign_keys=[buyer_id])
    seller = orm.relationship("User", foreign_keys=[seller_id])