from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, SubmitField, PasswordField, TextAreaField, FileField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

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

class ImageUploadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    image = FileField('Image File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Upload Image')

class EditPersonalDetails(FlaskForm):
    name = StringField('Name')
    title = StringField('Title')
    description = TextAreaField('Description')
    image = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Save changes')

class OfferForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'webp'], 'Images only!')])
    # form_path = StringField('Form Path') # er, later a selection of different types, not an MVP feature
    price = IntegerField('Price', validators=[DataRequired()])
    tag = SelectField('Tag')
    submit = SubmitField('Add Offer')
