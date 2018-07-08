#!/usr/bin/env python
import json
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange="topic_twitch_servitor",
                         exchange_type="topic")
routing_key = "topic.twitch.follows"
message = { "Salutation": "Hello world",
            "Response": "Hi new thing"}
channel.basic_publish(exchange='topic_twitch_servitor',
                      routing_key=routing_key,
                      body=json.dumps(message, ensure_ascii=False))
print(" [x] Sent '{}' to {}").format(message, routing_key)
connection.close()