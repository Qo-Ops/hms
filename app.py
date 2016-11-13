import os
from datetime import datetime
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
    is_owner = True if user_data['access_level'] == 2 else False
    print(is_owner)
    return User(user_data['id'], is_owner)


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
        form.password.data = generate_password_hash(form.password.data)

        c.execute("INSERT INTO users VALUES(DEFAULT, %(login)s, %(password)s, 1, %(email)s) RETURNING id;", form.data)
        params = (id, form.chain_name.data, form.location.data)
        c.execute("UPDATE locations SET admin_id=%s WHERE chain_name=%s AND location=%s", params)
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
        return redirect(url_for('login'))
    check_in = CheckinForm()
    current_reservations = get_current_reservations()
    return render_template('admin.html', location=location, check_in=check_in,
                           current_reservations=current_reservations)


@app.route('/book', methods=['POST', 'GET'])
def book():
    if request.method == 'GET':
        conn = get_db()
        c = conn.cursor()
        roomtype_id = int(request.args.get('roomtype_id'))
        print(roomtype_id)
        c.execute(queries.get_reservation_query, (roomtype_id,))
        booking = c.fetchone()
        dates = {"check_in": request.args.get('check-in'),
                 "check_out": request.args.get('check-out')}
        reservation = ReservationForm()
        reservation.roomtype_id.data = roomtype_id
        reservation.check_in.data = dates['check_in']
        reservation.check_out.data = dates['check_out']
        dates['days'] = daydelta(dates['check_out'], dates['check-in'])
        return render_template('booking_page.html', booking=booking,
                               dates=dates, reservation=reservation)
    reservation = ReservationForm()
    if reservation.validate_on_submit():
        try:
            db = get_db()
            c = db.cursor()

            c.execute("UPDATE rooms SET status='occupied' FROM (SELECT id FROM rooms WHERE room_type=%s LIMIT 1) AS r RETURNING r.id;",
                      (reservation.roomtype_id.data,))
            params = reservation.data
            params['room_id'] = c.fetchone()[0]
            c.execute("INSERT INTO visitors VALUES(DEFAULT, %(first_name)s, %(last_name)s, "
                      "%(ssn)s, %(country_code)s, %(email)s) RETURNING id;", reservation.data)
            params['visitor_id'] = c.fetchone()[0]
            c.execute("SELECT price FROM room_types WHERE id=%s", (int(reservation.roomtype_id.data),))
            price = int(c.fetchone()[0])
            params['total'] = daydelta(reservation.check_out.data, reservation.check_in.data) * price
            c.execute("INSERT INTO reservations VALUES(DEFAULT, %(total)s, %(check_in)s, "
                      "%(check_out)s, %(room_id)s, %(visitor_id)s)", params)
            db.commit()
        except Exception as e:
            app.logger.error(e)
            raise(e)
        return redirect('success.html')
    print(reservation.errors)


@app.route('/location', methods=['GET'])
def get_location():
    if current_user.owns(request.args.get('chain_name')):
        roomtype_form = RoomTypeForm(request.args)
        room_form = RoomForm()
        upload_form = UploadForm(request.args)
        conn = get_db()
        c = conn.cursor(cursor_factory=NamedTupleCursor)
        c.execute("SELECT id, name FROM room_types WHERE chain_name=%(chain_name)s AND location=%(location)s", request.args)
        room_form.room_type.choices = c.fetchall()
        info = {}
        c.execute(queries.total_income, request.args)
        info['income'] = c.fetchone()[0]
        c.execute(queries.count_rooms_query, request.args)
        info['total_rooms'] = c.fetchone()[0]
        c.execute(queries.count_occupied_rooms, request.args)
        info['occupied_rooms'] = c.fetchone()[0]
        return render_template('location.html', room_form=room_form, info=info,
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
        if check_password_hash(user_data['password'], data.password.data):
            login_user(User(user_data['id'], user_data['access_level'] == 2), remember=True)
            if current_user.is_owner:
                return redirect(url_for('owner_dashboard'))
            else:
                print(current_user.is_owner)
                print(current_user.id)
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
        admin_form = AdminForm()
        admin_form.chain_name.data = chain
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT chain_name, location, photo_path FROM locations WHERE chain_name=%s",
                   (chain,))
        locs = c.fetchall()
        location_form.chain_name.data = chain
        return render_template('chain.html', locations=locs,
                               new_admin=admin_form, new_location=location_form)


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
    check_in_form = CheckinForm()
    if check_in_form.validate():
        conn = get_db()
        c = conn.cursor()
        params = {'ssn': check_in_form.room_id.data,
                  'country': check_in_form.country.data
                  }
        c.execute(queries.check_in_query, params)    
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

def daydelta(stamp1, stamp2):
    date_format = "%Y-%m-%d"
    days = datetime.strptime(stamp1, date_format) - datetime.strptime(stamp2, date_format)
    return days.days

def get_current_reservations():
    conn = get_db()
    c = conn.cursor()
    c.execute(queries.current_reservations_query)
    return c.fetchall()

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
