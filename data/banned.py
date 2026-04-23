import sqlalchemy
from .db_session import SqlAlchemyBase


class BannedEmail(SqlAlchemyBase):
    __tablename__ = 'banned_emails'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    reason = sqlalchemy.Column(sqlalchemy.String, nullable=True)