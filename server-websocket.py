import json
from websocket_server import WebsocketServer

def client_connected(client, server):
	announce_string = "Hey all, {} has joined us".format(client['id'])
	server.send_message_to_all(announce_string)

def client_disconnected(client, server):
	announce_string = "Hey all, {} has disconnected from the server".format(client['id'])
	server.send_message_to_all(announce_string)

def broadcast_message(client, server, message):
    announce_string = json.loads(message)
    server.send_message_to_all(json.dumps(announce_string, ensure_ascii=False))

server = WebsocketServer(8000, host='127.0.0.1')
server.set_fn_message_received(broadcast_message)
server.run_forever()