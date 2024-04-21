from flask import Flask, render_template, url_for, request, redirect, flash, abort
from werkzeug.security import generate_password_hash
from data import db_session
from data.users import User
from data.comments import Comments
from forms.comments import NewsForm
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


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


@app.route('/comments', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comments = Comments()
        comments.title = form.title.data
        comments.content = form.content.data
        current_user.comments.append(comments)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/comment')
    return render_template('comments.html', form=form)


@app.route('/comments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        comments = db_sess.query(Comments).filter(Comments.id == id, Comments.user == current_user).first()
        if comments:
            form.title.data = comments.title
            form.content.data = comments.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comments = db_sess.query(Comments).filter(Comments.id == id, Comments.user == current_user).first()
        if comments:
            comments.title = form.title.data
            comments.content = form.content.data
            db_sess.commit()
            return redirect('/comment')
        else:
            abort(404)
    return render_template('comments.html',
                           form=form)


@app.route('/comments_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    comments = db_sess.query(Comments).filter(Comments.id == id,
                                              Comments.user == current_user).first()
    if comments:
        db_sess.delete(comments)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/comment')


def main():
    db_session.global_init("db/Web10.db")
    app.run()


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/catalog')
def catalog():
    return render_template('catalog.html')


@app.route('/card_tuc')
def card_tuc():
    return render_template('card_tuc.html')


@app.route('/card_mih')
def card_mih():
    return render_template('card_mih.html')


@app.route('/card_shambola')
def card_shambola():
    return render_template('card_shambola.html')


@app.route('/card_hramov')
def card_hramov():
    return render_template('card_hramov.html')


@app.route('/comment')
def comment():
    db_sess = db_session.create_session()
    comments = db_sess.query(Comments).filter()
    return render_template('comment.html', comments=comments)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/order')
def order():
    return render_template('orders.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


if __name__ == "__main__":
    main()