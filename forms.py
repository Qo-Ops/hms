from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField, DateField


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
    chain_name = StringField('chain_name', validators=[DataRequired()],
                       render_kw={"placeholder": "city", "type": "hidden"})