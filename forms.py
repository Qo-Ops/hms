from wtforms import validators
from flask_wtf import FlaskForm as Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, HiddenField, \
    IntegerField, SelectField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField, EmailField


class LoginForm(Form):
    login = StringField('login', validators=[DataRequired()],
                        render_kw={"placeholder": "login"})
    password = PasswordField('password', validators=[DataRequired()],
                             render_kw={"placeholder": "password"})


class RegistrationForm(Form):
    login = StringField('login', validators=[DataRequired()],
                        render_kw={"placeholder": "login"})
    password = PasswordField('password', validators=[DataRequired()],
                             render_kw={"placeholder": "password"})
    email = EmailField('email', validators=[DataRequired()],
                       render_kw={"placeholder": "email"})


class NewChainForm(Form):
    chain_name = StringField('chain_name', validators=[DataRequired()],
                             render_kw={"placeholder": "chain name",
                                        "class": "form-control"})


class AdminForm(Form):
    login = StringField('login', validators=[DataRequired()],
                        render_kw={"placeholder": "login", "class": "form-control"})
    password = PasswordField('password', validators=[DataRequired()],
                             render_kw={"placeholder": "password", "class": "form-control"})
    email = EmailField('email', validators=[DataRequired()],
                       render_kw={"placeholder": "email", "class": "form-control"})
    location = StringField('location', validators=[DataRequired()],
                           render_kw={"placeholder": "hotel",
                                      "class": "form-control"})


class SearchForm(Form):
    from_date = DateField('from_date', validators=[DataRequired()], format='%d/%m/%Y',
                          render_kw={"placeholder": "From", "class": "form-control"})
    to_date = DateField('to_date', validators=[DataRequired()], format='%d/%m/%Y',
                        render_kw={"placeholder": "To", "class": "form-control"})
    max_price = IntegerField('price',
                             render_kw={"placeholder": "Maximum price", "class": "form-control"})
    city = StringField('city', validators=[DataRequired()],
                       render_kw={"placeholder": "City", "class": "form-control"})


class LocationForm(Form):
    location = StringField('location', validators=[DataRequired()],
                           render_kw={"placeholder": "name of new hotel", "class": "form-control"})
    city = StringField('city', validators=[DataRequired()],
                       render_kw={"placeholder": "city", "class": "form-control"})
    chain_name = HiddenField('chain_name', validators=[DataRequired()],
                             render_kw={"placeholder": "city"})


class ReservationForm(Form):
    first_name = StringField('first_name', validators=[DataRequired()],
                             render_kw={"placeholder": "first name", "class": "form-control"})
    last_name = StringField('last_name', validators=[DataRequired()],
                             render_kw={"placeholder": "last name", "class": "form-control"})
    ssn = StringField('ssn', validators=[DataRequired()],
                             render_kw={"placeholder": "Social Security Number", "class": "form-control"})
    email = EmailField('email', validators=[DataRequired()],
                       render_kw={"placeholder": "E-mail", "class": "form-control"})
    country = StringField('country', validators=[DataRequired(), validators.length(max=3)],
                          render_kw={"placeholder": "Country code", "class": "form-control"})
    room_id = HiddenField('room_id', validators=[DataRequired()])
    check_in = DateField('check_in', validators=[DataRequired()])
    check_out = DateField('check_out', validators=[DataRequired()])


class RoomTypeForm(Form):
    chain_name = HiddenField('chain_name', validators=[DataRequired()])
    location = HiddenField('location', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()],
                       render_kw={"placeholder": "name", "class": "form-control"})
    price = IntegerField('price', validators=[DataRequired()],
                         render_kw={"placeholder": "price", "class": "form-control"})
    capacity = IntegerField('capacity', validators=[DataRequired()],
                            render_kw={"placeholder": "capacity", "class": "form-control"})


class RoomForm(Form):
    room_type = SelectField('id', validators=[DataRequired()],
                            render_kw={"class": "form-control"})
    roomNo = IntegerField('roomNo', validators=[DataRequired()],
                          render_kw={"placeholder": "number", "class": "form-control"})


class CheckinForm(Form):
    pass


class UploadForm(Form):
    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg'], 'Images only!')
    ])
    chain_name = HiddenField('chain_name', validators=[DataRequired()])
    location = HiddenField('location', validators=[DataRequired()])
