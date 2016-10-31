from functools import partial

import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, request, redirect, url_for, render_template, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from forms import LoginForm, RegistrationForm, NewChainForm

app = Flask(__name__)
app.config.from_object('config')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.session_protection = 'strong'


def get_db():
    from app import app
    db_info = (app.config['DB_HOST'], app.config['DB_NAME'], app.config['DB_USER'])
    if not hasattr(g, "postgres"):
        try:
            g.postgres = psycopg2.connect("host='{}' dbname='{}' user='{}'".format(*db_info),
                                          cursor_factory=DictCursor)
        except Exception as e:
            app.logger.error(str(e))
            raise e
    return g.postgres


from user import User


@lm.login_required
@app.route('/new-chain', methods=['POST'])
def new_chain():
    form = NewChainForm()
    if form.validate_on_submit():
        conn = get_db()
        c = conn.cursor()
        params = (form.chain_name.data, current_user.id)
        c.execute("INSERT INTO hotel_chains VALUES(DEFAULT, %s, %s)", params)


@lm.user_loader
def load_user(userid):
    conn = get_db()
    c = conn.cursor()
    user_data = None
    try:
        c.execute("SELECT id, access_level FROM users WHERE id=%s;", (userid,))
        user_data = c.fetchone()
        conn.commit()
        app.logger.debug("user with id {} was loaded".format(user_data[0]))
    except Exception as e:
        app.logger.debug("load_user has loaded no user")
        app.logger.error(str(e))
        raise e
    if user_data is None:
        return None
    return User(*user_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    data = LoginForm()
    if request.method == 'POST' and data.validate_on_submit():
        user_data = None
        try:
            conn = get_db()
            c = conn.cursor()
            print(data.login.data)
            c.execute("SELECT id, password, access_level FROM users WHERE login=%s;",
                      (data.login.data,))
            user_data = c.fetchone()
            conn.commit()
        except Exception as e:
            app.logger.error(str(e))
            raise e
        if user_data is None:
            return redirect(url_for('login'))
        if check_password_hash(user_data[1], data.password.data):
            login_user(User(user_data[0], user_data[2] == 2), remember=True)
            if current_user.is_owner:
                return redirect(url_for('owner_dashboard'))
            else:
                return redirect(url_for('admin'))
        else:
            flash("Sorry you entered wrong login and password combination")
    registration_form = RegistrationForm()
    return render_template('login.html', login_form=data, reg_form=registration_form)


@app.route('/registration', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES(DEFAULT, %s, %s, 2, %s);",
                  (form.login.data, generate_password_hash(form.password.data), form.email.data))
        conn.commit()
        return redirect(url_for('login'))
    return "whaat"


@login_required
@app.route('/admin', methods=['GET'])
def admin():
    location = current_user.get_managed_location()
    if location is None:
        return redirect(url_for('logout'))
    return render_template('admin.html', location=location)


@login_required
@app.route('/owner-dashboard', methods=['GET'])
def owner_dashboard():
    chains = current_user.get_owned_chains()
    return render_template('owner_dashboard.html', chains=chains)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.teardown_appcontext
def close_db(error):
    if error is not None:
        app.logger.error(error)
    db = getattr(g, 'postgres', None)
    if db is not None:
        db.close()
