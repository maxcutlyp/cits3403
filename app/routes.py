import flask
from flask_login import login_user, logout_user, login_required, current_user
from flask_socketio import send, join_room

import datetime
import time

from . import app, db, login, socketio
from .models import User, Session, Request, Submission, Message
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
            flask.session['last_err'] = f'Incorrect username or password.'
            flask.flash('Invalid username or password', 'error')
            return flask.redirect(flask.url_for('login'))

        login_user(user)

        # TODO: "next" param (like in flask-login docs)
        return flask.redirect(flask.url_for('index'))

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

        # TODO: "next" param
        return flask.redirect(flask.url_for('index'))

    error = flask.session.pop('last_err', None)
    return flask.render_template('signup.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()

    # TODO: "next" param
    return flask.redirect(flask.url_for('index'))

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

        messages_processed = [
            {
                'contents': message.text_content,
                'incoming': message.user_to == current_user.id,
            }
            for message in messages
        ]

    else:
        messages_processed = None

    return flask.render_template(
        'messages.html',
        recents=get_recents_processed(),
        messages=messages_processed,
        selected=user_id,
    )

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
        }
        for message in recents
    ]
    
    curr_time = datetime.datetime.now()
    for data in recent_data:
        for user_specific_time in recents:
            if user_specific_time[1] == data['user_id']:
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

@socketio.on('connect')
@login_required
def ws_connect():
    join_room(current_user.id)

@socketio.on('json')
@login_required
def ws_json(data: dict, *args):
    user_to = data.get('to', None)
    message = data.get('message', None)

    if user_to is None or message is None:
        print(f'Got unknown json data from socket: {data}')
        return

    send_message(user_to, message)

@login_required
def send_message(user_id: int, text_content: str):
    message = Message(
        user_from=current_user.id,
        user_to=user_id,
        timestamp=datetime.datetime.now(),
        text_content=text_content,
    )

    send(
        {
            'from': {
                'id': current_user.id,
                'display_name': current_user.display_name,
            },
            'message': text_content,
        },
        json=True,
        room=user_id,
    )

    db.session.add(message)
    db.session.commit()

