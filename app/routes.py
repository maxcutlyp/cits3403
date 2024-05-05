import flask
import os
from flask_login import login_user, logout_user, login_required, current_user

from . import app, db, login
from .models import User, Session, Image
from .forms import LoginForm, SignupForm, ImageUploadForm
from werkzeug.utils import secure_filename

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

@app.route('/gallery/', defaults={'artistID': None})
@app.route('/gallery/<int:artistID>')
def gallery(artistID):
    if artistID is None:
        artistID = current_user.id

    images = Image.query.filter_by(artist_id=artistID).all()
    artist = User.query.get(artistID)

    if not artist:
        return "Artist not found", 404
    return flask.render_template('gallery.html', images=images, artist=artist)

#Place to add an image to the database
@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    form = ImageUploadForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        image_file = form.image.data
        filename = secure_filename(image_file.filename)

        if current_user.is_authenticated:
            filename = secure_filename(image_file.filename)
            if filename != '':
                try:
                    username = current_user.display_name
                    folder_path = os.path.join('app/static/imgs/users/', current_user.id)
                    os.makedirs(folder_path, exist_ok=True)
                    image_file.save(os.path.join(folder_path, filename))

                    new_image = Image(
                        image_path=os.path.join('imgs/users/', current_user.id, filename),
                        title=form.title.data,
                        description=form.description.data,
                        artist_id=current_user.id
                    )
                    db.session.add(new_image)
                    db.session.commit()
                    flask.flash('Image successfully uploaded!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flask.flash(f'An error occurred: {str(e)}', 'error')
            else:
                flash('No file selected.', 'error')
        else:
            flash('You must be logged in to upload images.', 'error')
        return flask.redirect(flask.url_for('index'))


    return flask.render_template('upload_image.html', form=form)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}
