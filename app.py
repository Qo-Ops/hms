import os
from functools import partial

import psycopg2
from psycopg2.extras import DictCursor, NamedTupleCursor
from flask import Flask, request, redirect, url_for, render_template, flash, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from forms import *
import queries

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


@lm.user_loader
def load_user(userid):
    conn = get_db()
    c = conn.cursor()
    user_data = None
    try:
        c.execute("SELECT id, access_level FROM users WHERE id=%s;", (userid,))
        user_data = c.fetchone()
        conn.commit()
    except Exception as e:
        app.logger.debug("load_user has loaded no user")
        app.logger.error(str(e))
        raise e
    if user_data is None:
        return None
    return User(*user_data)


@app.route('/', methods=['GET'])
def main():
    return render_template('index.html', search=SearchForm())


@login_required
@app.route('/new-chain', methods=['POST'])
def add_chain():
    form = NewChainForm()
    if form.validate_on_submit():
        conn = get_db()
        c = conn.cursor()
        params = (form.chain_name.data, current_user.id)
        c.execute("INSERT INTO hotel_chains VALUES(%s, %s);", params)
        conn.commit()
    return redirect(url_for('owner_dashboard'))


@login_required
@app.route('/new-admin', methods=['POST'])
def add_admin():
    form = AdminForm()
    if form.validate_on_submit():
        conn = get_db()
        c = conn.cursor()
        params = (form.login.data, form.password.data, form.email.data)
        c.execute("INSERT INTO users VALUES(DEFAULT, %s, %s, 1, %s);", params)
        conn.commit()
    return redirect(url_for('owner_dashboard'))


@login_required
@app.route('/new-location', methods=['POST'])
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        conn = get_db()
        c = conn.cursor()
        default_path = url_for('static', filename='noimage.jpg')
        params = (form.chain_name.data, form.city.data, form.location.data, default_path)
        c.execute("INSERT INTO locations VALUES(%s, %s, %s, %s, NULL);", params)
        conn.commit()
    return redirect(url_for('owner_dashboard'))


@app.route('/new-reservation', methods=['POST', 'GET'])
def add_reservation():
    if request.method == 'GET':
        reservation = ReservationForm(request.args)
        return render_template('booking_page.html', reservation=reservation)
    reservation = ReservationForm()
    if reservation.validate_on_submit():
        try:
            db = get_db()
            c = db.cursor()
            c.execute("")
        except Exception as e:
            app.logger.error(e)
        return redirect('success.html')


@app.route('/new-room-type', methods=['POST'])
def add_room_type():
    roomtype_form = RoomTypeForm()
    if roomtype_form.validate_on_submit() and \
       current_user.owns(roomtype_form.chain_name.data):
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO room_types VALUES(DEFAULT, %(chain_name)s, %(location)s, %(name)s, %(price)s, %(capacity)s)", roomtype_form.data)
        conn.commit()
    return redirect(url_for('owner_dashboard'))


@app.route('/new-room', methods=['POST'])
def add_room():
    room_form = RoomForm()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO rooms VALUES(DEFAULT, %(room_type)s, %(roomNo)s, 'clean')",
              room_form.data)
    conn.commit()
    return redirect(url_for('owner_dashboard'))


@login_required
@app.route('/admin', methods=['GET'])
def admin():
    location = current_user.get_managed_location()
    if location is None:
        return redirect(url_for('logout'))
    return render_template('admin.html', location=location)


@app.route('/location', methods=['GET'])
def get_location():
    if current_user.owns(request.args.get('chain_name')):
        roomtype_form = RoomTypeForm(request.args)
        room_form = RoomForm()
        upload_form = UploadForm(request.args)
        conn = get_db()
        c = conn.cursor(cursor_factory=NamedTupleCursor)
        params = (request.args.get('chain_name'), request.args.get('location'))
        c.execute("SELECT id, name FROM room_types WHERE chain_name=%s AND location=%s", params)
        room_form.room_type.choices = c.fetchall()
        return render_template('location.html', room_form=room_form,
                               roomtype_form=roomtype_form, upload_form=upload_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    data = LoginForm()
    if request.method == 'POST' and data.validate_on_submit():
        user_data = None
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT id, password, access_level FROM users WHERE login=%s;",
                      (data.login.data,))
            user_data = c.fetchone()
            conn.commit()
        except Exception as e:
            app.logger.error(str(e))
            raise e
        if user_data is None:
            flash("Wrong login and password combination")
            return redirect(url_for('login'))
        if check_password_hash(user_data[1], data.password.data):
            login_user(User(user_data[0], user_data[2] == 2), remember=True)
            if current_user.is_owner:
                return redirect(url_for('owner_dashboard'))
            else:
                return redirect(url_for('admin'))
        flash("Wrong login and password combination")
    registration_form = RegistrationForm()
    return render_template('login.html', login_form=data, reg_form=registration_form)


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_required
@app.route('/chain', methods=['GET'])
def locations_by_chain():
    chain = request.args.get('name', None)
    if current_user.owns(chain):
        location_form = LocationForm()
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT chain_name, location, photo_path FROM locations WHERE chain_name=%s",
                   (chain,))
        locs = c.fetchall()
        # info = {}
        # c.execute("")
        # info['income'] = c.fetchone()
        # c.execute("")
        # info['total_rooms'] = c.fetchone()
        # c.execute("")
        # info['busy_rooms'] = c.fetchone()
        location_form.chain_name.data = chain
        return render_template('chain.html', locations=locs,
                               new_admin=AdminForm(), new_location=location_form)


@login_required
@app.route('/owner-dashboard', methods=['GET'])
def owner_dashboard():
    chains = current_user.get_owned_chains()

    return render_template('owner_dashboard.html', chains=chains,
                           new_chain=NewChainForm(), new_admin=AdminForm())


@app.route('/registration', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users VALUES(DEFAULT, %s, %s, 2, %s);",
                  (form.login.data,
                   generate_password_hash(form.password.data), form.email.data))
        conn.commit()
        return redirect(url_for('login'))
    return "whaat"


@app.route('/check-in', methods=['POST'])
def check_in():
    form = CheckinForm()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM rooms WHERE status='clean' OR status='dirty'")
    
    return redirect(url_for('admin'))


@app.route('/upload-location-pic', methods=['POST'])
def set_location_pic():
    form = UploadForm()
    if form.validate_on_submit() and current_user.owns(form.chain_name.data):
        try:
            path = get_location_pic_path(form.chain_name.data, form.location.data)
            form.image.data.save(path)
            conn = get_db()
            c = conn.cursor()
            params = (path, form.chain_name.data, form.location.data)
            c.execute("UPDATE locations SET photo_path=%s WHERE chain_name=%s AND location=%s", params)
            conn.commit()
        except:
            conn.rollback()
    return redirect(url_for('get_location', chain_name=form.chain_name.data,
                    location=form.location.data))


@app.route('/search', methods=['GET'])
def search():
    search = SearchForm(request.args)
    if search.validate():
        conn = get_db()
        c = conn.cursor()
        params = {'check_in': search.from_date.data,
                  'check_out': search.to_date.data,
                  'max_price': search.max_price.data,
                  'city': search.city.data
                  }
        c.execute(queries.search_query, params)
        results = c.fetchall()
        return render_template('search.html', results=results,
                               search=search)
    return render_template('search.html')



def get_location_pic_path(chain_name, location):
    filename = chain_name + location + ".jpg"
    return os.path.join(app.config['UPLOAD_FOLDER'], 'location-pics', filename)

@app.teardown_appcontext
def close_db(error):
    if error is not None:
        app.logger.error(error)
    db = getattr(g, 'postgres', None)
    if db is not None:
        db.close()
