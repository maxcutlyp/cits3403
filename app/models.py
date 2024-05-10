# This file declares some classes and functions for manipulating the server database.
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from . import db, login

#Class to define and store information on users in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # UserId, Primary key, automatically increments
    email = db.Column(db.String(120), index=True, unique=True)
    display_name = db.Column(db.String(64), nullable=False)
    hashed_password = db.Column(db.String(128))
    artist_title = db.Column(db.String(128)) # Used only by artist users to store their "MO"
    artist_description = db.Column(db.Text) # Used only by artist users to store a text description of themselves.

    #Set a user's password, (Stores as a hash for very obvious security reasons)
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    #Verify if a supplied password matches the one stored in the database
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

@login.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))

#Class to define and store information on images submitted by artists (And potentially reference images from users)
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(100), nullable=False) #TODO: (For security reasons) Consider storing the DATA CONTENT of the image as a string, to avoid allowing users to save a file to server storage
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    artist = db.relationship('User', backref=db.backref('images', lazy=True))

#Class to store a user's session ID information, allowing a user to be signed in after refreshing the page.
#TODO: Add functions to generate a new sessionId
#TODO: Add in the time of last activity on a sessionID, and functions to check if it is still valid
class Session(db.Model):
    # Schema: (userId | sessionId | ... )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #UserId, Foreign key, corresponding to user table
    session_id = db.Column(db.String(128), unique=True, primary_key=True) #Unique Session ID to represent each user's session

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_from = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, nullable=False)
    text_content = db.Column(db.Text, nullable=False)
    # TODO: attachments e.g. images

    __table_args__ = (
        db.CheckConstraint('user_from != user_to'),
    )

