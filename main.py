import os

from data.banned import BannedEmail
from db_config import create_admin_user

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from data import db_session
from flask import Flask, render_template, redirect, abort, request, current_app

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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
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
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    product = db_sess.query(Product)
    if "AnonymousUserMixin" not in str(current_user):
        return render_template("index.html", product=product, url="/profile", name_b=current_user.name)
    return render_template("index.html", product=product)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db_sess.query(BannedEmail).filter(BannedEmail.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Вы забанены на сайте")
        user = User(
            name=form.name.data,
            email=form.email.data,
            age=form.age.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/profile")
@login_required
def profile():
    db_sess = db_session.create_session()
    product = db_sess.query(Product)
    return render_template("profile.html", product=product, url="/", name_b="Вернуться на главную")


@app.route("/purchase/<int:id>", methods=['GET', 'POST'])
@login_required
def purchase(id):
    db_sess = db_session.create_session()
    basket = db_sess.query(Basket).filter(Basket.user == current_user).first()
    if not basket:
        basket = Basket()
        basket.user_id = current_user.id
    b_item = db_sess.query(BasketItem).filter(BasketItem.product_id == id).first()
    product = db_sess.query(Product).filter(Product.id == id).first()
    if product:
        if not b_item:
            b_item = BasketItem()
            b_item.product_id = id
            b_item.basket_id = basket.id
            basket.basket_items.append(b_item)
            product.quantity -= 1
            db_sess.merge(basket)
            db_sess.commit()
        else:
            b_item.quantity += 1
            db_sess.merge(b_item)
            product.quantity -= 1
            db_sess.commit()
    else:
        abort(404)
    return redirect("/")


@app.route("/ban/<int:item_id>", methods=['GET', 'POST'])
@login_required
def ban(item_id):
    if current_user.role == "a":
        form = BanForm()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == item_id).first()
        if user and user != current_user and current_user.role == "a":
            if form.validate_on_submit():
                print(form.password_for_ban.data)
                if form.password_for_ban.data != "123ban":
                    return render_template('ban.html', title='Забанить пользователя',
                                           form=form,
                                           message="Вы ввели код неправильно")
                else:
                    ban = BannedEmail()
                    ban.email = user.email
                    ban.reason = form.reason.data
                    db_sess.delete(user)
                    db_sess.add(ban)
                    db_sess.commit()
                    return redirect("/")
        else:
            abort(404)
        return render_template('ban.html', user=user, form=form, title="Забанить пользователя", url="/",
                               name_b="Вернутся на главную")
    else:
        abort(404)


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.role == "a":
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id != 1).all()
        return render_template("admin.html", users=users, url="/profile", name_b="Вернуться в профиль")
    else:
        abort(404)


@app.route("/basket", methods=['GET', 'POST'])
@login_required
def basket():
    db_sess = db_session.create_session()
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


@app.route("/quantity/<int:item_id>", methods=['GET', 'POST'])
@login_required
def quantity(item_id):
    form = QuantityForm()
    db_sess = db_session.create_session()
    basket_item = db_sess.query(BasketItem).filter(BasketItem.product_id == item_id).first()
    product = db_sess.query(Product).filter(basket_item.product_id == Product.id).first()
    if basket_item:
        if form.validate_on_submit():
            if form.quantity.data > product.quantity:
                basket_item.quantity = product.quantity
            elif form.quantity.data <= 0:
                basket_item.quantity = 1
            else:
                basket_item.quantity = form.quantity.data
            product.quantity -= basket_item.qantity
            db_sess.merge(basket_item)
            db_sess.commit()
            return redirect("/basket")
    else:
        abort(404)
    return render_template("quantity.html", form=form)


@app.route("/buy", methods=['GET', 'POST'])
@login_required
def buy():
    db_sess = db_session.create_session()
    basket = db_sess.query(Basket).filter(Basket.user == current_user).first()
    basket_item = db_sess.query(BasketItem).filter(basket.user == current_user).all()
    if basket_item:
        for i in basket_item:
            product = db_sess.query(Product).filter(i.product_id == Product.id).first()
            if i.quantity * product.price <= current_user.balance:
                user = db_sess.query(User).filter(product.user_id == User.id).first()
                current_user.balance -= i.quantity * product.price
                user.balance += i.quantity * product.price
                db_sess.merge(user)
            else:
                return redirect("/balance")
        for j in basket_item:
            db_sess.delete(j)
        db_sess.merge(current_user)
        db_sess.delete(basket)
        db_sess.commit()
        return redirect("/")
    return redirect("/")


@app.route("/balance", methods=["GET", "POST"])
@login_required
def balance():
    form = BalanceForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        current_user.balance += form.balance.data
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect("/")
    return render_template("balance.html", form=form, name_b="Вернуться на главную", url="/")


@app.route('/products', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = Product()

        product.title = form.title.data
        product.content = form.content.data
        product.price = form.price.data
        product.quantity = form.quantity.data
        product.wtype = form.wtype.data
        product.weaponry = form.weaponry.data
        product.building_material = form.building_material.data
        product.tool = form.tool.data
        product.used = form.used.data
        product.user_id = current_user.id
        if form.image.data:
            image = form.image.data
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(filepath)
                product.image_path = 'images/' + filename
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
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id,
                                                Product.user == current_user
                                                ).first()
        if product:
            form.title.data = product.title
            form.content.data = product.content
            form.price.data = product.price
            form.quantity.data = product.quantity
            form.wtype.data = product.wtype
            form.weaponry.data = product.weaponry
            form.building_material.data = product.building_material
            form.tool.data = product.tool
            form.used.data = product.used
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id,
                                                Product.user == current_user
                                                ).first()
        if product:
            product.title = form.title.data
            product.content = form.content.data
            product.price = form.price.data
            product.quantity = form.quantity.data
            product.wtype = form.wtype.data
            product.weaponry = form.weaponry.data
            product.building_material = form.building_material.data
            product.tool = form.tool.data
            product.used = form.used.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('product.html',
                           title='Редактирование товара',
                           form=form
                           )


@app.route('/products_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def product_delete(id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id,
                                            Product.user == current_user
                                            ).first()
    if product:
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
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
