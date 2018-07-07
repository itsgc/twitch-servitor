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
from flask import url_for
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
app.config['SERVER_NAME'] = "apple.didgt.info"
app.config['PREFERRED_URL_SCHEME'] = "https"
settings = make_settings("settings.yml")
auth_creds = make_auth("creds.yml")

def get_user_info(auth_token):
    url = "https://api.twitch.tv/helix/users"
    headers = { 'Authorization': 'Bearer ' + auth_token}
    payload = { "login": "karmik"}
    r = requests.get(url=url, headers=headers, params=payload)
    return r.json()

def subscribe_followers(user_id, client_id):
    callback_url = url_for('webhook', _external=True)
    headers = { "Client-ID": client_id }
    sub_url = "https://api.twitch.tv/helix/webhooks/hub"
    base_topic_url = "https://api.twitch.tv/helix/users/follows"
    payload = { "to_id": user_id }

    url = urlparse.urlparse(base_topic_url)
    urllist = [ url.scheme, url.netloc, url.path, None, urllib.urlencode(payload), url.fragment ]
    topic_url = urlparse.urlunparse(urllist)
    subscribe_payload = {"hub.callback": callback_url,
                         "hub.mode": "subscribe",
                         "hub.topic": topic_url,
                         "hub.lease_seconds": 3600}
    r = requests.post(url=sub_url, headers=headers, json=subscribe_payload)
    return r.text

@app.route("/")
def index():
    return redirect(get_auth_url(auth_creds))

@app.route("/twitch/authlistener")
def authlistener():
    twitch_code = request.args.get('code', '')
    twitch_tokens = get_access_tokens(twitch_code)
    user_data = get_user_info(twitch_tokens['access_token'])
    user_id = int(user_data['data'][0]['id'])
    print subscribe_followers(user_id, auth_creds['client_id'])
    return "OK"

@app.route("/twitch/webhook")
def webhook():
    webhook_payload = request.args
    try:
        webhook_challenge = webhook_payload['hub.challenge']
    except:
        webhook_challenge = "Fail"

    print webhook_payload
    return webhook_challenge

