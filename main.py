import os

from data.banned import BannedEmail
from db_config import create_admin_user

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from data import db_session
from flask import Flask, render_template, redirect, abort, request, current_app, flash
from forms.unban import UnbanForm
from data.basket import Basket
from data.basket_item import BasketItem
from data.comments import Comment
from data.product import Product
from data.users import User
from forms.balance import BalanceForm
from forms.ban import BanForm
from forms.comment import CommentForm
from forms.login import LoginForm
from forms.products import ProductForm
from forms.quantity import QuantityForm
from forms.user import RegisterForm
import base64
from forms.add_product import AddProductForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, авторизуйтесь для доступа к этой странице.'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def main():
    db_session.global_init("db/products.sqlite")

    db_sess = db_session.create_session()
    if not db_sess.query(User).first():
        create_admin_user()
    db_sess.close()

    app.run()


@app.route("/")
def index():
    with db_session.create_session() as db_sess:
        products = db_sess.query(Product).all()

        for product in products:
            if product.image_data is not None:
                product.image_data = base64.b64encode(product.image_data).decode("utf-8")
            else:
                product.image_data = None

        if current_user.is_authenticated:
            return render_template("index.html", product=products, url="/profile", name_b=current_user.name)
        return render_template("index.html", product=products)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")

        with db_session.create_session() as db_sess:
            existing_user = db_sess.query(User).filter(User.email == form.email.data).first()
            if existing_user:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message=f"Пользователь с почтой {form.email.data} уже зарегистрирован")

            banned = db_sess.query(BannedEmail).filter(BannedEmail.email == form.email.data).first()
            if banned:
                reason = f" Причина: {banned.reason}" if banned.reason else ""
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message=f"Эта почта заблокирована.{reason}")

            user = User(
                name=form.name.data,
                email=form.email.data,
                age=form.age.data,
                city=form.city.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()

            return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route("/profile")
@login_required
def profile():
    with db_session.create_session() as db_sess:
        products = db_sess.query(Product).filter(Product.user_id == current_user.id).all()

        for product in products:
            if product.image_data:
                product.image_data = base64.b64encode(product.image_data).decode("utf-8")

        return render_template("profile.html", product=products)


@app.route("/purchase/<int:id>", methods=['GET', 'POST'])
@login_required
def purchase(id):
    with db_session.create_session() as db_sess:  # ← добавить with
        basket = db_sess.query(Basket).filter(Basket.user == current_user).first()
        if not basket:
            basket = Basket()
            basket.user_id = current_user.id
            db_sess.add(basket)
            db_sess.commit()

        b_item = db_sess.query(BasketItem).filter(BasketItem.product_id == id).first()
        product = db_sess.query(Product).filter(Product.id == id).first()

        if product:
            if not b_item:
                b_item = BasketItem()
                b_item.product_id = id
                b_item.basket_id = basket.id
                b_item.quantity = 1
                db_sess.add(b_item)
                db_sess.commit()
        else:
            abort(404)

    return redirect("/")


@app.route("/banned_list")
@login_required
def banned_list():
    if current_user.role != "a":
        abort(404)

    with db_session.create_session() as db_sess:  # ← добавить with
        banned_emails = db_sess.query(BannedEmail).all()
        return render_template("banned_list.html", banned_emails=banned_emails)


@app.route("/unban/<int:banned_id>", methods=['GET', 'POST'])
@login_required
def unban(banned_id):
    if current_user.role != "a":
        abort(404)

    form = UnbanForm()

    with db_session.create_session() as db_sess:  # ← добавить with
        banned_email = db_sess.query(BannedEmail).filter(BannedEmail.id == banned_id).first()

        if not banned_email:
            abort(404)

        if form.validate_on_submit():
            db_sess.delete(banned_email)
            db_sess.commit()
            return redirect("/banned_list")

        return render_template("unban.html", form=form, banned_email=banned_email)


@app.route("/ban/<int:item_id>", methods=['GET', 'POST'])
@login_required
def ban(item_id):
    if current_user.role != "a":
        abort(404)

    form = BanForm()

    with db_session.create_session() as db_sess:  # ← with автоматически закроет
        user = db_sess.query(User).filter(User.id == item_id).first()

        if not user or user == current_user:
            abort(404)

        if form.validate_on_submit():
            ban_record = BannedEmail()
            ban_record.email = user.email
            ban_record.reason = form.reason.data


            basket = db_sess.query(Basket).filter(Basket.user_id == user.id).first()
            if basket:
                db_sess.query(BasketItem).filter(BasketItem.basket_id == basket.id).delete()
                db_sess.delete(basket)


            db_sess.query(Product).filter(Product.user_id == user.id).delete()

            db_sess.query(Comment).filter(Comment.user_id == user.id).delete()

            db_sess.delete(user)
            db_sess.add(ban_record)
            db_sess.commit()
            return redirect("/admin")

        return render_template('ban.html', user=user, form=form, title="Забанить пользователя",
                               url="/", name_b="Вернуться на главную")


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role != "a":
        abort(404)

    with db_session.create_session() as db_sess:  # ← добавить with
        users = db_sess.query(User).filter(User.id != 1).all()
        return render_template("admin.html", users=users, url="/profile", name_b="Вернуться в профиль")


@app.route("/basket", methods=['GET', 'POST'])
@login_required
def basket():
    with db_session.create_session() as db_sess:  # ← добавить with
        basket = db_sess.query(Basket).filter(Basket.user_id == current_user.id).first()
        if basket:
            b_items = db_sess.query(BasketItem).filter(BasketItem.basket_id == basket.id).all()
            t_price = 0
            t_quantity = 0
            for item in b_items:
                t_price += item.product.price * item.quantity
                t_quantity += item.quantity
            return render_template("basket.html", basket_items=b_items, basket=basket,
                                   t_price=t_price, t_quantity=t_quantity)
        else:
            return render_template("basket.html", basket=basket)


# @app.route("/quantity/<int:item_id>", methods=['GET', 'POST'])
# @login_required
# def quantity(item_id):
#    form = QuantityForm()
#    db_sess = db_session.create_session()
#    basket_item = db_sess.query(BasketItem).filter(BasketItem.product_id == item_id).first()
#    product = db_sess.query(Product).filter(basket_item.product_id == Product.id).first()
#    if basket_item:
#        if form.validate_on_submit():
#            if form.quantity.data > product.quantity:
#                basket_item.quantity = product.quantity
#            elif form.quantity.data <= 0:
#                basket_item.quantity = 1
#            else:
#                basket_item.quantity = form.quantity.data
#            product.quantity -= basket_item.qantity
#            db_sess.merge(basket_item)
#            db_sess.commit()
#            return redirect("/basket")
#    else:
#        abort(404)
#    return render_template("quantity.html", form=form)


@app.route("/buy", methods=['GET', 'POST'])
@login_required
def buy():
    with db_session.create_session() as db_sess:  # ← добавить with
        basket = db_sess.query(Basket).filter(Basket.user == current_user).first()
        if not basket:
            return redirect("/")

        basket_items = db_sess.query(BasketItem).filter(BasketItem.basket_id == basket.id).all()

        if basket_items:
            for item in basket_items:
                product = db_sess.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    if product.price <= current_user.balance:
                        seller = db_sess.query(User).filter(User.id == product.user_id).first()
                        current_user.balance -= product.price
                        seller.balance += product.price
                        db_sess.delete(product)
                        db_sess.commit()
                    else:
                        return redirect("/balance")

            for item in basket_items:
                db_sess.delete(item)
            db_sess.delete(basket)
            db_sess.commit()

        return redirect("/")


@app.route("/balance", methods=["GET", "POST"])
@login_required
def balance():
    form = BalanceForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:  # ← добавить with
            current_user.balance += form.balance.data
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect("/")
    return render_template("balance.html", form=form, name_b="Вернуться на главную", url="/")


@app.route('/products', methods=['GET', 'POST'])
@login_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:
            product = Product()

            product.title = form.title.data
            product.content = form.content.data
            product.price = form.price.data
            product.quantity = 1
            product.breed = form.breed.data
            product.color = form.color.data
            product.age_months = form.age_months.data
            product.gender = form.gender.data
            product.vaccinated = (form.vaccinated.data == 'yes')
            product.user_id = current_user.id
            product.image_data = form.image.data.read()

            db_sess.add(product)
            db_sess.commit()
            return redirect('/profile')

    return render_template('product.html', title='Добавление товара', form=form)


@app.route('/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def add_comment(id):
    form = CommentForm()
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(id)
    comment = db_sess.query(Comment).filter(Comment.product_id == id).first()
    if comment:
        db_sess.delete(comment)
        db_sess.commit()
    if not product:
        abort(404)
    if form.validate_on_submit():
        comment = Comment()
        comment.user_id = current_user.id
        comment.product_id = product.id
        comment.rate = int(form.rate.data)
        comment.content = form.content.data
        db_sess.add(comment)
        db_sess.commit()
        product.calculate_rating()
        db_sess.commit()
        return redirect("/")
    return render_template('comment.html', form=form, product=product,
                           name_b="Вернуться на главную", url="/")


@app.route('/comment_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_delete(id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == id).first()
    if comment:
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/comments')


@app.route('/comments/<int:item_id>')
def comment(item_id):
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.product_id == item_id).all()
    product = db_sess.query(Product).filter(Product.id == item_id).first()
    return render_template("comments.html", comments=comments,
                           product=product, name_b="Вернуться на главную", url="/")


@app.route('/products/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    form = ProductForm()
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()

    if product and (product.user == current_user or current_user.role == "a"):
        if request.method == "GET":
            form.title.data = product.title
            form.content.data = product.content
            form.price.data = product.price
            form.breed.data = product.breed
            form.color.data = product.color
            form.age_months.data = product.age_months
            form.gender.data = product.gender
            form.vaccinated.data = 'yes' if product.vaccinated else 'no'

            product_image = None
            if product.image_data:
                product_image = base64.b64encode(product.image_data).decode("utf-8")

        if form.validate_on_submit():
            product.title = form.title.data
            product.content = form.content.data
            product.price = form.price.data
            product.breed = form.breed.data
            product.color = form.color.data
            product.age_months = form.age_months.data
            product.gender = form.gender.data
            product.vaccinated = (form.vaccinated.data == 'yes')

            if form.image.data and form.image.data.filename:
                product.image_data = form.image.data.read()

            db_sess.commit()
            return redirect('/')

        product_image = None
        if product.image_data:
            product_image = base64.b64encode(product.image_data).decode("utf-8")

        return render_template('product.html', title='Редактирование товара', form=form, product_image=product_image)
    else:
        abort(404)


@app.route('/products_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_delete(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()


    if product and (product.user == current_user or current_user.role == "a"):
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    with db_session.create_session() as db_sess:
        return db_sess.get(User, user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with db_session.create_session() as db_sess:

            banned = db_sess.query(BannedEmail).filter(BannedEmail.email == form.email.data).first()
            if banned:
                reason = f" Причина: {banned.reason}" if banned.reason else ""
                return render_template('login.html',
                                       message=f"Ваш email заблокирован.{reason}",
                                       form=form)

            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")

            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
