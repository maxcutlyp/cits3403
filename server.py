import flask
from models import db, User, Session, Request, Submission, Ranking

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables in database if they don't exist
    app.run()
