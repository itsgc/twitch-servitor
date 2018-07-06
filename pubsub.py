import re
import requests
import websocket
from yaml import load

try:
    import thread
except ImportError:
    import _thread as thread
import time

with open('creds.yml', 'r') as credsfile:
    creds = load(credsfile)
    twitch_token = creds['twitch_irc_token']

with open('settings.yml', 'r') as settingsfile:
    settings = load(settingsfile)

def get_channel_id(auth_token):
    url = 'https://api.twitch.tv/kraken/channel'
    headers = {'Accept': 'application/vnd.twitchtv.v5+json',
               'Authorization': 'OAuth ' + auth_token}
    r = requests.get(url=url, headers=headers)
    return r.text

def check_message(ws, message):
    print message
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
        time.sleep(5)
        time.sleep(1)
        ws.send(irc_channel_command)
        time.sleep(1)
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    websocket_server = settings['websocket_pubsub_server']
    # ws = websocket.WebSocketApp(websocket_server,
    #                          on_message = on_message,
    #                          on_error = on_error,
    #                          on_close = on_close,
    #                          )
    # ws.on_open = on_open(ws, settings, twitch_token)
    # ws.run_forever(ping_interval=300, ping_timeout=10)
    print get_channel_id(twitch_token)