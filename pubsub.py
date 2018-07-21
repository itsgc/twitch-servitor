import json
import re
import websocket
from os import environ
from yaml import load

import servitor_utils

try:
    import thread
except ImportError:
    import _thread as thread
import time

settings = servitor_utils.make_settings(environ.get('SETTINGS_FILE'))
auth_data = servitor_utils.make_auth(environ.get('SECRETS_FILE'))
pubsub_auth_data = servitor_utils.make_auth(environ.get('PUBSUB_SECRETS_FILE'))


def check_message(ws, message):
    try:
        parsed_message = json.loads(message)
        if parsed_message['type'] == "MESSAGE":
            sub_payload = parsed_message['data']['message']
            sub_type = sub_payload['context']
            sub_data = {"type": sub_type,
                        "months": sub_payload['months'],
                        "message": sub_payload['sub_message']['message']}

            if "subgift" in sub_type:
                recipient = sub_payload['recipient_display_name']
                sub_data['recipient'] = recipient

            amqp_payload = {"type": "pubsub",
                            "sub-type": "SUBSCRIPTION",
                            "sub-type-username": sub_payload['display_name'],
                            "message": sub_data}
            servitor_utils.send_amqp_notice(host=settings['amqp_server'],
                                            exchange=settings['amqp_exchange'],
                                            topic=settings['topics']['pubsub'],
                                            message=amqp_payload)
        print parsed_message
    except Exception as e:
        print "failed parsing message: {}".format(e)

    return True

def check_error(ws, message):
    print message
    return True

def on_message(ws, message):
    if check_message(ws, message):
        return
    elif check_error(ws, message):
        return

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws, settings, auth_token):
    def run(*args):
        time.sleep(1)
        request_channel_subs = "channel-subscribe-events-v1." + settings['channel_id']
        payload = {
                    "type": "LISTEN",
                    "data": {
                        "topics": [ request_channel_subs ],
                        "auth_token": auth_token
                    }
                  }
        ws.send(json.dumps(payload))
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    websocket.enableTrace(True)
    auth_data['auth_endpoint'] = None
    dispenser_url = settings['dispenser_url']
    pubsub_secret = pubsub_auth_data['pubsub_secret']
    toolkit = servitor_utils.TwitchTools(auth_data)
    twitch_token_payload =  toolkit.get_pubsub_token(secret=pubsub_secret, dispenser_url=dispenser_url)
    twitch_token = twitch_token_payload['access_token']
    websocket_server = settings['websocket_pubsub_server']
    ws = websocket.WebSocketApp(websocket_server,
                             on_message = on_message,
                             on_error = on_error,
                             on_close = on_close,
                             )
    ws.on_open = on_open(ws, settings, twitch_token)
    ws.run_forever(ping_interval=300, ping_timeout=10)
