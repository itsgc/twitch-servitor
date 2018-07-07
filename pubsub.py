import re
import requests
import websocket
from yaml import load

try:
    import thread
except ImportError:
    import _thread as thread
import time

def make_auth(credsfile_path):
    with open(credsfile_path, 'r') as credsfile:
        return load(credsfile)

def make_settings(settingsfile_path):
    with open(settingsfile_path, 'r') as settingsfile:
        return load(settingsfile)

def get_auth_token(auth_creds):
    grant_type = "client_credentials"
    payload = { "client_id": auth_creds['client_id'],
                       "client_secret": auth_creds['client_secret'],
                       "grant_type": grant_type,
                       "scope": "channel_read" }
    url = "https://id.twitch.tv/oauth2/token"
    r = requests.post(url=url, data=payload)
    return r.json()

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
    settings = make_settings("settings.yml")
    auth_creds = make_auth("creds.yml")
    websocket_server = settings['websocket_pubsub_server']
    # ws = websocket.WebSocketApp(websocket_server,
    #                          on_message = on_message,
    #                          on_error = on_error,
    #                          on_close = on_close,
    #                          )
    # ws.on_open = on_open(ws, settings, twitch_token)
    # ws.run_forever(ping_interval=300, ping_timeout=10)
    auth_token = get_auth_token(auth_creds)['access_token']
    print get_channel_id(auth_token)
    # print get_channel_id(twitch_token)