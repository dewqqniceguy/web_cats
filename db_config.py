from werkzeug.security import generate_password_hash

from data import db_session
from data.users import User


def create_admin_user():
    user = User()
    user.name = "Админ"
    user.email = "admin@cat.com"
    user.hashed_password = generate_password_hash("123456")
    user.age = 52
    user.city = "Канаш"
    user.role = "a"
    user.balance = 10000000
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()
