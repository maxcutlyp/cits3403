import flask
from models import db, User, Image

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/gallery/<int:artistID>')
def gallery(artistID):
    images = Image.query.filter_by(artist_id=artistID).all()
    artist = User.query.get(artistID)

    if not artist:
        return "Artist not found", 404
    return flask.render_template('gallery.html', images=images, artist=artist)

# Function for populating a new database with initial values for testing
@app.route('/debuginit')
def debuginit():
    # Creating a new user
    artist = User(username='Enth', email='sig@howeville.com', artist_title="Computer Scientist & Digital Artist", artist_description="Hacker, Artist, Mango Enthusiast.\n An egotistical loser who uses himself as a debug example on a CITS project.\n Has no friends.")
    db.session.add(artist)
    db.session.commit()

    # Adding images for the user
    image1 = Image(image_path='images/society.jpg', title='N-Bracket Comic', description='A reflection upon society.\n Lorem Ipsum Text here.', artist_id=artist.id)
    image2 = Image(image_path='images/dogdog.png', title='dogdog', description='It\'s DogDog!', artist_id=artist.id)

    db.session.add(image1)
    db.session.add(image2)
    db.session.commit()

    return "done!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables in database if they don't exist
    app.run()


