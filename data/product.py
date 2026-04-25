import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Product(SqlAlchemyBase):
    __tablename__ = 'product'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # имя котика или заголовок
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # описание характера
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Float, default=0.00)
    quantity = sqlalchemy.Column(sqlalchemy.Integer)  # количество (если продают сразу выводок)

    # новые поля для Мяу-Маркета
    breed = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # порода
    color = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # окрас
    age_months = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # возраст в месяцах
    gender = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Пол
    vaccinated = sqlalchemy.Column(sqlalchemy.Boolean, default=False)  # привит ли

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image_data = sqlalchemy.Column(sqlalchemy.BLOB)

    user = orm.relationship('User', back_populates='product')
    comments = orm.relationship('Comment', back_populates='product')

    def calculate_rating(self):
        if not self.comments:
            self.rating = 0.00
            return

        total_rating = sum(comment.rate for comment in self.comments)
        self.rating = float(total_rating) / len(self.comments)