from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


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
                           render_kw={"placeholder": "administrated hotel",
                                      "class": "form-control"})
