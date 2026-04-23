import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class BasketItem(SqlAlchemyBase):
    __tablename__ = 'basket_item'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('product.id'))
    basket_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('basket.id'))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)

    basket = orm.relationship("Basket", back_populates="basket_items")
    product = orm.relationship("Product")
