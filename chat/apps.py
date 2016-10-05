import json
import redis

from django.apps import AppConfig

from tornado import web, websocket


class ChatConfig(AppConfig):
    name = 'chat'


users = {}


def broadcast(message):
    for handler in users.values():
        handler.write_message(message)


class WebSocketHandler(websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._username = None

    def check_origin(self, origin):
        return True

    def open(self, *args):
        token = self.get_argument('token')

        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        rstore = redis.Redis(connection_pool=pool)
        username = rstore.get('token:{}'.format(token)).decode('utf8')
        if username:
            self._username = username
            self.stream.set_nodelay(True)

            # all users presences to me
            for username in users:
                self.write_message(json.dumps({
                    'type': 'presence',
                    'from': 'room/{}'.format(username),
                    'status': 'online',
                }))

            users[self._username] = self

            # own presence to everyone
            broadcast(json.dumps({
                'type': 'presence',
                'from': 'room/{}'.format(self._username),
                'status': 'online',
            }))

        else:
            self.close(reason='Access denied')

    def on_message(self, message):
        data = json.loads(message)
        data['from'] = 'room/{}'.format(self._username)
        room, _, username = data['to'].partition('/')
        if username:
            if username in users:
                users[username].write_message(json.dumps(data))
        else:
            broadcast(json.dumps(data))

    def on_close(self):
        if self._username in users:
            del users[self._username]

            # own presence to everyone
            broadcast(json.dumps({
                'type': 'presence',
                'from': 'room/{}'.format(self._username),
                'status': 'offline',
            }))


tornado_app = web.Application([
    (r'/', WebSocketHandler),
])
