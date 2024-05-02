# This file declares some classes and functions for manipulating the server database.
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

#Class to define and store information on users in the database
class User(db.Model):
    # Schema: [ userId | username | email | password (hashed) ]
    id = db.Column(db.Integer, primary_key=True)  # UserId, Primary key, automatically increments
    username = db.Column(db.String(64), unique=True, index=True)  # Username: Max size of 64, must be unique
    email = db.Column(db.String(120), unique=True, index=True)  # Email must also be unique
    hashed_password = db.Column(db.String(128))  # Password, hashed for security
    artist_title = db.Column(db.String(128)) # Used only by artist users to store their "MO"
    artist_description = db.Column(db.Text) # Used only by artist users to store a text description of themselves.

    #Set a user's password, (Stores as a hash for very obvious security reasons)
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    #Verify if a supplied password matches the one stored in the database
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

#Class to define and store information on images submitted by artists (And potentially reference images from users)
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(100), nullable=False) #TODO: (For security reasons) Consider storing the DATA CONTENT of the image as a string, to avoid allowing users to save a file to server storage
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    artist = db.relationship('User', backref=db.backref('images', lazy=True))
