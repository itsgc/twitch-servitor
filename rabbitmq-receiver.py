#!/usr/bin/env python
import json
import pika
import requests
import time
import websocket

import servitor_utils

settings = servitor_utils.make_settings("settings.yml")

def send_ws_message(message, settings):
    websocket_server = settings['websocket_local_server']
    ws = websocket.create_connection(websocket_server)
    ws.send(message)
    ws.recv()
    ws.close()

def callback(ch, method, properties, body):
    amqp_payload = json.loads(body)
    message_payload = {"topic": method.routing_key,
                       "message": amqp_payload}
    send_ws_message(json.dumps(message_payload, ensure_ascii=False))


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings['amqp_server']))
    channel = connection.channel()
    login_message = {"type": "status",
                     "message": "rabbitmq-receiver online"}
    send_ws_message(json.dumps(login_message))
    channel.exchange_declare(exchange=settings['amqp_exchange'],
                             exchange_type="topic")
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    binding_keys = ["topic.twitch.follows", "topic.twitch.subscriptions", "topic.twitch.hosts"]
    for binding_key in binding_keys:
        channel.queue_bind(exchange=settings['amqp_exchange'],
                           queue=queue_name,
                           routing_key=binding_key)
        queue_subscribe_message = {"topic": "status",
                                   "message": "rabbitmq-receiver subscribed to {}".format(binding_key)}
        send_ws_message(json.dumps(queue_subscribe_message))
    channel.basic_consume(callback, queue=queue_name,
                          no_ack=True)
    channel.start_consuming()
