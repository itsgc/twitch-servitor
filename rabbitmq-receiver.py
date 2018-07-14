#!/usr/bin/env python
import json
import pika
import requests
import time
import websocket

import utils


def send_ws_message(message):
    websocket_server = "ws://localhost:8000"
    ws = websocket.create_connection(websocket_server)
    ws.send(message)
    ws.recv()
    ws.close()

def callback(ch, method, properties, body):
    aqmp_payload = json.loads(body)
    message_payload = {"topic": method.routing_key,
                       "message": json.dumps(aqmp_payload)}
    print(message_payload)
    send_ws_message(json.dumps(message_payload))


if __name__ == "__main__":
    settings = utils.make_settings("settings.yml")
    auth_creds = utils.make_auth("creds.yml")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    login_message = {"type": "status",
                     "message": "rabbitmq-receiver online"}
    send_ws_message(json.dumps(login_message))
    channel.exchange_declare(exchange="topic_twitch_servitor",
                             exchange_type="topic")
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    binding_keys = ["topic.twitch.follows", "topic.twitch.subscriptions", "topic.twitch.hosts"]
    for binding_key in binding_keys:
        channel.queue_bind(exchange="topic_twitch_servitor",
                           queue=queue_name,
                           routing_key=binding_key)
        queue_subscribe_message = {"topic": "status",
                                   "message": "rabbitmq-receiver subscribed to {}".format(binding_key)}
        send_ws_message(json.dumps(queue_subscribe_message))

    channel.basic_consume(callback, queue=queue_name,
                          no_ack=True)
    channel.start_consuming()
