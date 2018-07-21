import json
from os import environ
from websocket_server import WebsocketServer

import servitor_utils


def client_connected(client, server):
	announce_string = "Hey all, {} has joined us".format(client['id'])
	server.send_message_to_all(announce_string)

def client_disconnected(client, server):
	announce_string = "Hey all, {} has disconnected from the server".format(client['id'])
	server.send_message_to_all(announce_string)

def broadcast_message(client, server, message):
    announce_string = json.loads(message)
    server.send_message_to_all(json.dumps(announce_string, ensure_ascii=False))

settings = servitor_utils.make_settings(environ.get('SETTINGS_FILE'))
server = WebsocketServer(port=settings['websocket_local_port'], host=settings['websocket_local_server'])
server.set_fn_message_received(broadcast_message)
server.run_forever()