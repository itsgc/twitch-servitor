import re
import requests
import urllib
import urlparse
import websocket
from flask import Flask
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
    payload = { "client_id": auth_creds['client_id'],
                "redirect_uri": "https://apple.didgt.info",
                "response_type": "code",
                "scope": "channel_read" }
    url = "https://id.twitch.tv/oauth2/authorize"
    # r = requests.get(url=url, params=payload)
    return urlparse.urljoin(url , urllib.urlencode(payload))

def get_channel_id(auth_token):
    url = 'https://api.twitch.tv/kraken/channel'
    headers = {'Accept': 'application/vnd.twitchtv.v5+json',
               'Authorization': 'OAuth ' + auth_token}
    r = requests.get(url=url, headers=headers)
    return r.text

app = Flask(__name__)
settings = make_settings("settings.yml")
auth_creds = make_auth("creds.yml")

@app.route("/")
def index():
    output = get_auth_token(auth_creds)
    print output
    return output
