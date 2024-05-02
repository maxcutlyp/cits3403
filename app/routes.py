import flask
from flask_login import login_user, logout_user, login_required, current_user

from . import app, db, login
from .models import User, Session, Image
from .forms import LoginForm, SignupForm

@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            # incorrect password - TODO: tell user
            return flask.redirect(flask.url_for('login'))

        login_user(user)

        # TODO: "next" param (like in flask-login docs)
        return flask.redirect(flask.url_for('index'))

    return flask.render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            # email already exists - TODO: tell user
            return flask.redirect(flask.url_for('signup'))

        user = User(
            email=form.email.data,
            display_name=form.display_name.data,
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        # TODO: "next" param
        return flask.redirect(flask.url_for('index'))

    return flask.render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()

    # TODO: "next" param
    return flask.redirect(flask.url_for('index'))

@app.route('/messages/')
def route_messages_blank():
    return route_messages(None)

@app.route('/messages/<string:username>')
def route_messages(username: str | None):
    # Most of this function is just generating dummy data
    # TODO: pull from database

    lorem = '''\
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam a hendrerit tellus. Cras vitae erat tristique, ultricies justo eget, ultricies purus. Etiam sit amet sem scelerisque, laoreet elit sit amet, convallis lacus. In aliquet orci sit amet pharetra consectetur. Nam vel lectus in enim maximus auctor. Donec sit amet tempor tortor. Nunc dolor odio, placerat et pharetra sed, semper id turpis. Ut sit amet risus ut nunc pulvinar imperdiet. Aliquam suscipit, nisl in malesuada mattis, urna ante maximus arcu, sit amet feugiat lectus neque ut quam. Ut magna neque, accumsan non feugiat at, malesuada vitae libero. Mauris lacinia ultrices ornare. Nam suscipit fermentum sem ut convallis. Cras dictum, neque vitae ultrices viverra, turpis ipsum auctor nulla, sed rutrum nisl odio mattis mauris. Mauris lorem nisi, dignissim non diam id, lacinia facilisis felis. Nunc ac auctor est. In hac habitasse platea dictumst. Ut gravida laoreet libero, vitae iaculis felis elementum eget. Fusce nec pellentesque dolor. Mauris a justo vitae nibh eleifend dictum. Etiam quis pharetra ipsum. Nunc at ex augue. Aliquam sed quam ante. Quisque sit amet nibh eu tortor porta rhoncus vel sed diam. Suspendisse faucibus rutrum fringilla. Ut id convallis diam, vitae imperdiet urna. Integer quis auctor urna. Sed pulvinar, elit ut tincidunt aliquet, tortor sapien sodales ex, eu auctor eros nisl in sapien. Fusce finibus metus vel semper laoreet. Donec sed vehicula est. Sed bibendum dignissim urna ornare vehicula. Aliquam fermentum pretium suscipit. Duis in urna erat. Aliquam id euismod purus. Morbi euismod porttitor posuere. In posuere sed erat ut varius. Ut mauris est, tempus in vestibulum vitae, fermentum nec tortor. Fusce vitae enim a diam iaculis placerat. Praesent at elit eu lorem feugiat tincidunt. Nam laoreet erat turpis, quis dignissim ex blandit vitae. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam sodales, quam quis dignissim sodales, neque nibh commodo mauris, sed tincidunt justo ex non nisl. Praesent tincidunt id turpis sed lacinia. Sed urna tortor, commodo in dui et, hendrerit tempus libero. Nullam facilisis fringilla nisi id lacinia. Quisque pharetra faucibus justo, et elementum ex. Duis vitae ante cursus, fermentum mauris non, feugiat est. Pellentesque sem nunc, tincidunt et mi eu, maximus elementum quam. Vivamus tempor mattis lorem, id facilisis leo rutrum pharetra. Nulla efficitur augue sit amet mollis elementum. Proin id justo at est cursus imperdiet vel sed tortor. In in eros in justo vestibulum finibus. Curabitur augue quam, mattis in posuere nec, lacinia non risus. Donec malesuada sed tellus non iaculis. Nunc elementum suscipit justo, vel cursus lorem pharetra vel. Nunc tempus volutpat turpis ac pharetra. Praesent et vestibulum nulla. Praesent et neque euismod, consectetur ex nec, rhoncus purus.\
'''.split(' ')
    lorems = lambda n : ' '.join(lorem[(start := random.randrange(len(lorem))):start+n])

    # yoinked from https://dzone.com/articles/name-lists-generating-test
    fnames = ['john','robert','michael','william','david','richard','mary','patricia','linda','barbara','elizabeth','jennifer']
    snames = ['smith','johnson','williams','brown','jones','miller','davis','garcia','rodriguez','wilson','martinez']

    # import here because all the code relying on it is temporary anyway
    import random

    recents = [
        {
            'username': random.choice(fnames) + random.choice(snames),
            'preview': lorems(20),
        }
        for _ in range(20)
    ]

    if username is None:
        messages = None
    else:
        messages = [
            {
                'incoming': bool(random.randint(0, 1)),
                'contents': lorems(random.randint(1, 30))
            }
            for _ in range(random.randint(1, 40))
        ]

        if username not in [ x['username'] for x in recents ]:
            recents.insert(0, {
                'username': username,
                'preview': lorems(20),
            })

    return flask.render_template(
        'messages.html',
        recents=recents,
        messages=messages, # Note: most recent messages first
        selected=username,
    )

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
    artist = User(display_name='Enth', email='sig@howeville.com', artist_title="Computer Scientist & Digital Artist", artist_description="Hacker, Artist, Mango Enthusiast.\n An egotistical loser who uses himself as a debug example on a CITS project.\n Has no friends.")
    db.session.add(artist)
    db.session.commit()

    # Adding images for the user
    image1 = Image(image_path='imgs/society.jpg', title='N-Bracket Comic', description='A reflection upon society.\n Lorem Ipsum Text here.', artist_id=artist.id)
    image2 = Image(image_path='imgs/dogdog.png', title='dogdog', description='It\'s DogDog!', artist_id=artist.id)

    db.session.add(image1)
    db.session.add(image2)
    db.session.commit()

    return "done!"
