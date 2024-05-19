import flask
import os
import datetime
import time
import base64
import urllib

from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import send, join_room

from . import app, db, login, socketio
from .models import User, Session, Image, Message, Offer, Tag, Attachment
from .forms import LoginForm, SignupForm, ImageUploadForm, EditPersonalDetails, OfferForm
from werkzeug.utils import secure_filename

@app.route('/')
def index():

    sort_attribute = flask.request.args.get('sort')
    allowed_tags = flask.request.args.getlist('tags')

    tag_list = Tag.query.all()

    tag_names = [tag.name for tag in tag_list]

    allowed_tags = [tag.id for tag in tag_list if tag.name in allowed_tags]

    match sort_attribute:
        case None | "new":
            order_orientation = Offer.timestamp.desc()
        case "old":
            order_orientation = Offer.timestamp.asc()
        case "cheap":
            order_orientation = Offer.min_price.asc()
        case "expensive":
            order_orientation = Offer.min_price.desc()

    query = db.session.query(
        Offer.title, Offer.description, Offer.artist_id, Offer.image_path, Offer.min_price, Offer.max_price
    ).order_by(
        order_orientation
    )

    if allowed_tags:
        query = query.filter(Offer.tag_id.in_(allowed_tags))

    offers = query.all()
    
    return flask.render_template('index.html', tags=tag_names, offers=offers)

def valid_url(url: str | None):
    if url is None:
        return True

    parsed = urllib.parse.urlparse(url)
    return parsed.scheme == '' and parsed.netloc in ('', flask.request.host)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flask.session['last_err'] = f'Incorrect username or password.'
            flask.flash('Invalid username or password', 'error')
            return flask.redirect(flask.url_for('login'))

        login_user(user)

        nxt = flask.request.args.get('next')
        if not valid_url(nxt):
            return flask.abort(400)

        return flask.redirect(nxt or flask.url_for('index'))

    error = flask.session.pop('last_err', None)
    return flask.render_template('login.html', form=form, error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flask.session['last_err'] = f'Email "{form.email.data}" is already taken.'
            return flask.redirect(flask.url_for('signup'))

        user = User(
            email=form.email.data,
            display_name=form.display_name.data,
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        nxt = flask.request.args.get('next')
        if not valid_url(nxt):
            return flask.abort(400)

        return flask.redirect(nxt or flask.url_for('index'))

    error = flask.session.pop('last_err', None)
    return flask.render_template('signup.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()

    nxt = flask.request.args.get('next')
    if not valid_url(nxt):
        return flask.abort(400)

    return flask.redirect(nxt or flask.url_for('index'))

@app.route('/messages/')
@login_required
def route_messages_blank():
    return route_messages(None)

@app.route('/messages/<int:user_id>')
@login_required
def route_messages(user_id: int | None):
    if user_id is not None:
        # Sorted most recent first to play nicely the frontend (see messages.css).
        messages = Message.query\
            .filter(
                ((Message.user_from == current_user.id) & (Message.user_to == user_id)) |
                ((Message.user_from == user_id) & (Message.user_to == current_user.id))
            )\
            .order_by(db.desc(Message.timestamp))\
            .all()
        
        messages_to_read = Message.query\
            .filter(
                ((Message.user_from == user_id) & (Message.user_to == current_user.id))
            )\
            .order_by(db.desc(Message.timestamp))\
            .all()
        

        for msg in messages_to_read:
            msg.is_read = 1
        
        db.session.commit()

        messages_processed = [
            {
                'contents': msg.text_content,
                'incoming': msg.user_to == current_user.id,
                'timestamp': message_timestamp(msg.timestamp),
                'attachments': Attachment.query.filter_by(message_id=msg.id),
            }
            for msg in messages
        ]

    else:
        messages_processed = None

    return flask.render_template(
        'messages.html',
        recents=get_recents_processed(),
        messages=messages_processed,
        selected=user_id,
    )

def message_timestamp(timestamp: datetime.datetime):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day_endings = ["st", "nd", "rd"] + ["th"] * 28

    if timestamp.date() == datetime.datetime.today().date():
        return f"{timestamp.hour}:{timestamp.minute:02}"

    return f"{timestamp.day}{day_endings[timestamp.day - 1]} {months[timestamp.month]}"

@app.route('/gallery/')
@login_required
def my_gallery():
    return gallery(current_user.id)

@app.route('/gallery/<int:artistID>')
def gallery(artistID):
    offers = Offer.query.filter_by(artist_id=artistID).all()
    offers_data = [offer.to_dict() for offer in offers]
    images = Image.query.filter_by(artist_id=artistID).all()
    artist = User.query.get(artistID)

    if not artist:
        return "Artist not found", 404
    return flask.render_template('gallery.html', images=images, artist=artist, offers=offers_data)

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
                    folder_path = os.path.join('app/static/imgs/users/', str(current_user.id))
                    os.makedirs(folder_path, exist_ok=True)
                    image_file.save(os.path.join(folder_path, filename))

                    new_image = Image(
                        image_path=os.path.join('imgs/users/', str(current_user.id), filename),
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
        return flask.redirect(flask.url_for('gallery'))


    return flask.render_template('upload_image.html', form=form)

@app.route('/add_offer', methods=['GET', 'POST'])
def add_offer():

    tag_list = Tag.query.all()
    
    form = OfferForm()

    form.tag.choices = [(tag.id, tag.name) for tag in tag_list]

    if form.validate_on_submit():
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            os.makedirs('app/static/imgs/offers/', exist_ok=True)
            filepath = os.path.join('imgs/offers/', filename)
            form.image.data.save(os.path.join('app/static/', filepath))
        else:
            filepath = None

        offer = Offer(
            artist_id=current_user.id,
            timestamp=datetime.datetime.utcnow(),
            title=form.title.data,
            description=form.description.data,
            image_path=filepath,
            # form_path=form.form_path.data
            min_price=0.0,
            max_price=0.0, #SET LATER
            tag_id=form.tag.data
        )
        db.session.add(offer)
        db.session.commit()
        flask.flash('Your offer has been created!', 'success')
        return flask.redirect(flask.url_for('gallery'))
    return flask.render_template('add_offer.html', title='Add Offer', form=form, tags=tag_list)

@app.route('/edit_details', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditPersonalDetails()

    if form.validate_on_submit():

        user_details = User.query.get(current_user.id)

        user_details.display_name = form.name.data if form.name.data else current_user.display_name
        user_details.artist_title = form.title.data if form.title.data else current_user.artist_title
        user_details.artist_description = form.description.data if form.description.data else current_user.artist_description
        if form.image.data:
            filename = user_details.id
            os.makedirs('app/static/imgs/profiles/', exist_ok=True)
            filepath = os.path.join('imgs/profiles/', filename)
            form.image.data.save(os.path.join('app/static/', filepath))
        db.session.commit()

        return flask.redirect(flask.url_for('gallery'))

    return flask.render_template('edit_details.html', form=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp'}

@login_required
def get_recents_processed():

    # SELECT user_from, user_to, MAX(timestamp) AS timestamp, text_content
    # FROM Message
    # WHERE user_from=$(current_user.id) OR user_to=$(current_user.id)
    # GROUP BY (user_from, user_to)
    # ORDER BY timestamp DESC

    recents = db.session.query(
            Message.user_from,
            Message.user_to,
            db.func.max(Message.timestamp).label('timestamp'),
            Message.text_content,
            Message.is_read
        )\
        .filter((Message.user_from == current_user.id) | (Message.user_to == current_user.id))\
        .group_by(Message.user_from, Message.user_to)\
        .order_by(db.desc('timestamp'))\
        .all()

    # `recents` contains both the most recent message sent from `current_user` to every
    # other user, and the most recent message sent from every other user to `current_user`,
    # ordered by most recent message first.
    # For any given pair of ((current_user -> other_user), (other_user -> current_user))
    # messages, we are only interested in the most recent (i.e. earlier in the list) one.
    # So we loop through and remove any messages whose conterpart we've already seen.
    # If you can think of a SQL-only solution to this, let me know.

    seen_pairs = set()
    i = 0
    while i < len(recents):
        message = recents[i]

        # (from, to)
        if (message.user_from, message.user_to) in seen_pairs:
            recents.pop(i)
            continue

        # (to, from)
        seen_pairs.add((message.user_to, message.user_from))
        i += 1

    recent_data = [
        {
            'user_id': (other_user_id := ({ message.user_from, message.user_to } - { current_user.id }).pop()),
            'display_name': User.query.get(other_user_id).display_name,
            'preview': message.text_content,
            'is_read': message.is_read or message.user_from == current_user.id,
        }
        for message in recents
    ]

    curr_time = datetime.datetime.now()
    for data in recent_data:
        for user_specific_time in recents:
            if data['user_id'] in user_specific_time[0:2]:
                date_and_time = user_specific_time[2]
                epoch_time = date_and_time.timestamp()
                time_diff = time.time() - epoch_time
                if curr_time.year == date_and_time.year:
                    if curr_time.day == date_and_time.day:
                        if time_diff < 3600:
                            if time_diff < 60: # Within the last minute
                                data['time'] = "now"
                            else: # Within the last hour
                                data['time'] = f"{int(time_diff / 60)}m ago"
                        else: # Same day
                            data['time'] = f"{date_and_time.hour}:{date_and_time.minute:02}"
                    else: # Same year
                        data['time'] = f"{date_and_time.strftime('%B')} {date_and_time.day}"
                else: # Different year
                    data['time'] = f"{date_and_time.strftime('%B')} {date_and_time.year}"

    return recent_data

@app.route('/components/messages-sidebar')
@login_required
def messages_sidebar():
    try:
        selected = int(flask.request.args['selected'])
    except (KeyError, ValueError):
        selected = None

    return flask.render_template(
        'components/messages-sidebar.html',
        recents=get_recents_processed(),
        selected=selected,
    )

@login_required
def render_message(message_id: int, for_user_id=None):
    if for_user_id is None:
        for_user_id = current_user.id

    message = Message.query.get(message_id)

    if for_user_id not in (message.user_from, message.user_to):
        return 403, 'Not your message!'

    return flask.render_template(
        'components/message.html',
        incoming=message.user_to == for_user_id,
        text_content=message.text_content,
        timestamp=message_timestamp(message.timestamp),
        attachments=Attachment.query.filter_by(message_id=message_id),
    )

@app.route('/attachments', methods=['POST'])
@login_required
def add_message_attachment():
    files = [ file for _, file in flask.request.files.items(multi=True) ]
    print(files)
    attachments = [ Attachment(filename=file.filename) for file in files ]
    db.session.add_all(attachments)
    db.session.commit()

    # Note: not storing in /static because we only want auth'd users to access them.
    # (See get_message_attachment())
    folder_path = os.path.join(app.instance_path, 'attachments')
    os.makedirs(folder_path, exist_ok=True)

    ids = []
    for file, attachment in zip(files, attachments):
        db.session.refresh(attachment)
        ids.append(attachment.id)

        # This probably becomes problematic if someone uploads a very large file.
        file.save(os.path.join(folder_path, str(attachment.id)))

    return ids, 200

@app.route('/attachments/<int:attachment_id>', methods=['GET'])
@login_required
def get_message_attachment(attachment_id: int):
    attachment = Attachment.query.get_or_404(attachment_id)
    message = Message.query.get(attachment.message_id)

    if current_user.id not in (message.user_from, message.user_to):
        return 403, 'Not your attachment!'

    return flask.send_file(
        os.path.join(app.instance_path, 'attachments', str(attachment_id)),
        as_attachment=True,
        download_name=attachment.filename,
    )

@socketio.on('connect')
@login_required
def ws_connect():
    join_room(current_user.id)

@socketio.on('json')
@login_required
def ws_json(data: dict, *args):
    user_to = data.get('to', None)
    message = data.get('message', None)
    attachments = data.get('attachments', None)

    if None in (user_to, message, attachments):
        print(f'Got unknown json data from socket: {data}')
        return

    return render_message(send_message(user_to, message, attachments))

@login_required
def send_message(user_id: int, text_content: str, attachment_ids: list[int]):
    message = Message(
        user_from=current_user.id,
        user_to=user_id,
        timestamp=datetime.datetime.now(),
        text_content=text_content,
    )

    db.session.add(message)
    db.session.flush()
    db.session.refresh(message)

    valid_attachments = []
    for attachment_id in attachment_ids:
        attachment = Attachment.query.get(attachment_id)
        if attachment.message_id is None:
            attachment.message_id = message.id
            valid_attachments.append(attachment)
    db.session.commit()

    message_data = {
        'from': {
            'id': current_user.id,
            'display_name': current_user.display_name,
        },
        'message': text_content,
        'attachments': [ attachment.id for attachment in valid_attachments ],
        'message_html': render_message(message.id, for_user_id=user_id),
    }

    message_data['notification_html'] = flask.render_template(
        'components/notification.html',
        data=message_data
    )

    send(
        message_data,
        json=True,
        room=user_id,
    )

    return message.id
