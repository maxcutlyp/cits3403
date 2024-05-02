from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, EqualTo

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Log in')
    # TODO: "remember me" field

class SignupForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    display_name = StringField('Display name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('password_confirm')])
    password_confirm = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Sign up')
