# This file declares some classes and functions for manipulating the server database.
# TODO: Elaborate on the documentation
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

#Class to define and store information on users in the database
class User(db.Model):
    # Schema: [ userId | username | email | site-wide score | password (hashed) ]
    id = db.Column(db.Integer, primary_key=True) #UserId, Primary key, TODO: Add the keyword making this incremental, so it does not need to be set each time.
    username = db.Column(db.String(64), primary_key=True, index=True, unique=True) #Username: Max size of 64, one per user
    email = db.Column(db.String(120), index=True, unique=True)
    total_points = db.Column(db.Integer, default=0)
    hashed_password = db.Column(db.String(128))

    #Set a user's password, (Stores as a hash for very obvious security reasons)
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    #Verify if a supplied password matches the one stored in the database
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    #TODO: Add function for creating a new user, removing a user who unregisters, adding points to a user and removing points from a user
    #      And checking availible points, And a function to get a username's useid, and vice versa


#Class to store a user's session ID information, allowing a user to be signed in after refreshing the page.
#TODO: Add functions to generate a new sessionId
#TODO: Add in the time of last activity on a sessionID, and functions to check if it is still valid
class Session(db.Model):
    # Schema: (userId | sessionId | ... )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #UserId, Foreign key, corresponding to user table
    session_id = db.Column(db.String(128), unique=True, primary_key=True) #Unique Session ID to represent each user's session

#Class to store all user requests on the request board application.
#TODO: Add functions
class Request(db.Model):
    # Schema: (requestId | requesting userId | request Title | request description )
    id = db.Column(db.Integer, primary_key=True) #Request ID, TODO: Add the keyword making this incremental, so it does not need to be set each time.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #UserId, Foreign key, corresponding to the id of user table
    title = db.Column(db.String(128)) #The name of this request
    description = db.Column(db.Text) #The description of this request

#Class to store all user submissions to each user submitted request
#TODO: Add functions
#TODO: Add a function that pulls all submissions made for any given request
#TODO: Assign each submission a rating, that is a unique number for each request id
class Submission(db.Model):
    # Schema: (submissionId | associated requestId | submitting userId | submission content | submission ranking)
    id = db.Column(db.Integer, primary_key=True) #The id of the submission TODO: Add the keyword making this incremental, so it does not need to be set each time.
    request_id = db.Column(db.Integer, db.ForeignKey('request.id')) #foreign key id representing the request a submission responds to
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) #UserId, Foreign key, corresponding to user table
    content = db.Column(db.Text) # Content of a submission
    ranking = db.Column(db.Integer) #TODO: Make unique with request ID
