import json
import re
import requests
import time
import urllib
import urlparse
import websocket
from flask import Flask
from flask import redirect
from flask import request
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

def get_auth_url(auth_creds):
    payload = { "client_id": auth_creds['client_id'],
                "redirect_uri": "https://apple.didgt.info/twitch/authlistener",
                "response_type": "code",
                "scope": "channel_read" }
    url = urlparse.urlparse("https://id.twitch.tv/oauth2/authorize")
    urllist = [ url.scheme, url.netloc, url.path, None, urllib.urlencode(payload), url.fragment ]
    return urlparse.urlunparse(urllist)
    # r = requests.get(url=url, params=payload)
    # return urlparse.urljoin(url , urllib.urlencode(payload))

def get_access_tokens(intermediate_code):
     payload = {
                "client_id": auth_creds['client_id'],
                "client_secret": auth_creds['client_secret'],
                "code": intermediate_code,
                "grant_type": "authorization_code",
                "redirect_uri": "https://apple.didgt.info/twitch/authlistener"
     }
     url = "https://id.twitch.tv/oauth2/token"
     r = requests.post(url=url, data=payload)
     return r.json()

def get_channel_id(auth_token):
    url = 'https://api.twitch.tv/kraken/channel'
    headers = {'Accept': 'application/vnd.twitchtv.v5+json',
               'Authorization': 'OAuth ' + auth_token}
    r = requests.get(url=url, headers=headers)
    return r.text

app = Flask(__name__)
settings = make_settings("settings.yml")
auth_creds = make_auth("creds.yml")

def get_user_info(auth_token):
    url = "https://api.twitch.tv/helix/users"
    headers = { 'Authorization': 'Bearer ' + auth_token}
    payload = { "login": "karmik"}
    r = requests.get(url=url, headers=headers, params=payload)
    return r.json()

@app.route("/")
def index():
    return redirect(get_auth_url(auth_creds))

@app.route("/twitch/authlistener")
def authlistener():
    twitch_code = request.args.get('code', '')
    twitch_tokens = get_access_tokens(twitch_code)
    user_data = get_user_info(twitch_tokens['access_token'])
    user_id = user_data['data'][0]['id']
    print user_id
    return "OK"

