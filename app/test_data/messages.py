import random
import sys
import datetime

from .. import app, db
from ..models import User, Message

def main(n: int = 20):
    lorem = '''\
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam a hendrerit tellus. Cras vitae erat tristique, ultricies justo eget, ultricies purus. Etiam sit amet sem scelerisque, laoreet elit sit amet, convallis lacus. In aliquet orci sit amet pharetra consectetur. Nam vel lectus in enim maximus auctor. Donec sit amet tempor tortor. Nunc dolor odio, placerat et pharetra sed, semper id turpis. Ut sit amet risus ut nunc pulvinar imperdiet. Aliquam suscipit, nisl in malesuada mattis, urna ante maximus arcu, sit amet feugiat lectus neque ut quam. Ut magna neque, accumsan non feugiat at, malesuada vitae libero. Mauris lacinia ultrices ornare. Nam suscipit fermentum sem ut convallis. Cras dictum, neque vitae ultrices viverra, turpis ipsum auctor nulla, sed rutrum nisl odio mattis mauris. Mauris lorem nisi, dignissim non diam id, lacinia facilisis felis. Nunc ac auctor est. In hac habitasse platea dictumst. Ut gravida laoreet libero, vitae iaculis felis elementum eget. Fusce nec pellentesque dolor. Mauris a justo vitae nibh eleifend dictum. Etiam quis pharetra ipsum. Nunc at ex augue. Aliquam sed quam ante. Quisque sit amet nibh eu tortor porta rhoncus vel sed diam. Suspendisse faucibus rutrum fringilla. Ut id convallis diam, vitae imperdiet urna. Integer quis auctor urna. Sed pulvinar, elit ut tincidunt aliquet, tortor sapien sodales ex, eu auctor eros nisl in sapien. Fusce finibus metus vel semper laoreet. Donec sed vehicula est. Sed bibendum dignissim urna ornare vehicula. Aliquam fermentum pretium suscipit. Duis in urna erat. Aliquam id euismod purus. Morbi euismod porttitor posuere. In posuere sed erat ut varius. Ut mauris est, tempus in vestibulum vitae, fermentum nec tortor. Fusce vitae enim a diam iaculis placerat. Praesent at elit eu lorem feugiat tincidunt. Nam laoreet erat turpis, quis dignissim ex blandit vitae. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam sodales, quam quis dignissim sodales, neque nibh commodo mauris, sed tincidunt justo ex non nisl. Praesent tincidunt id turpis sed lacinia. Sed urna tortor, commodo in dui et, hendrerit tempus libero. Nullam facilisis fringilla nisi id lacinia. Quisque pharetra faucibus justo, et elementum ex. Duis vitae ante cursus, fermentum mauris non, feugiat est. Pellentesque sem nunc, tincidunt et mi eu, maximus elementum quam. Vivamus tempor mattis lorem, id facilisis leo rutrum pharetra. Nulla efficitur augue sit amet mollis elementum. Proin id justo at est cursus imperdiet vel sed tortor. In in eros in justo vestibulum finibus. Curabitur augue quam, mattis in posuere nec, lacinia non risus. Donec malesuada sed tellus non iaculis. Nunc elementum suscipit justo, vel cursus lorem pharetra vel. Nunc tempus volutpat turpis ac pharetra. Praesent et vestibulum nulla. Praesent et neque euismod, consectetur ex nec, rhoncus purus.\
'''.split(' ')
    lorems = lambda n : ' '.join(lorem[(start := random.randrange(len(lorem))):start+n])

    users = User.query.all()

    if len(users) < 2:
        print(f'ERROR: Not enough users in DB (need 2, found {len(users)}).')
        raise SystemExit

    now = datetime.datetime.now()
    seconds_in_a_week = 60 * 60 * 24 * 7

    for _ in range(n):
        user_from, user_to = random.sample(users, k=2)

        message = Message(
            user_from=user_from.id,
            user_to=user_to.id,
            timestamp=now - datetime.timedelta(seconds=random.randint(0, seconds_in_a_week)),
            text_content=lorems(random.randint(1, 30)),
            is_read=0
        )

        db.session.add(message)

    db.session.commit()

if __name__ == '__main__':
    n_messages = int(sys.argv[1]) if len(sys.argv) > 1 else None

    with app.app_context():
        if n_messages is None:
            main()
        else:
            main(n_messages)
