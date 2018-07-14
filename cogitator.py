import json
import pika
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

import utils

try:
    import thread
except ImportError:
    import _thread as thread
import time

def get_auth_url(auth_creds):
    payload = { "client_id": auth_creds['client_id'],
                "redirect_uri": "https://apple.didgt.info/twitch/authlistener",
                "response_type": "code",
                "scope": "channel_read" }
    url = urlparse.urlparse("https://id.twitch.tv/oauth2/authorize")
    urllist = [ url.scheme, url.netloc, url.path, None, urllib.urlencode(payload), url.fragment ]
    return urlparse.urlunparse(urllist)

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

def send_aqmp_notice(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange="topic_twitch_servitor",
                         exchange_type="topic")
    routing_key = "topic.twitch.follows"
    message = { "type": message['sub-type'],
                "username": message['sub-type-username'],
                "message": message['message']}
    channel.basic_publish(exchange='topic_twitch_servitor',
                      routing_key=routing_key,
                      body=json.dumps(message, ensure_ascii=False))
    connection.close()

app = Flask(__name__)
app.config['SERVER_NAME'] = "apple.didgt.info"
app.config['PREFERRED_URL_SCHEME'] = "https"
settings = utils.make_settings("settings.yml")
auth_creds = utils.make_auth("creds.yml")

def get_user_info(auth_token, type, value):
    url = "https://api.twitch.tv/helix/users"
    headers = { 'Authorization': 'Bearer ' + auth_token}
    payload = { type: value}
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
    user_data = get_user_info(twitch_tokens['access_token'], type="login", value="karmik")
    user_id = int(user_data['data'][0]['id'])
    print subscribe_followers(user_id, auth_creds['client_id'])
    return "OK"

@app.route("/twitch/webhook", methods = ['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        webhook_args = request.args
        try:
            webhook_challenge = webhook_args['hub.challenge']
        except:
            webhook_challenge = "Fail"
        return webhook_challenge
    elif request.method == 'POST':
        if request.json:
            webhook_body = request.get_json()
            user_data = get_user_info(auth_creds['twitch_irc_token'], type="id", value=webhook_body['data']['from_id'])
            print json.dumps(webhook_body, indent=4, sort_keys=True)
            print json.dumps(user_data)
            payload = { "sub-type": "follow",
                        "sub-type-username": user_data['data'][0]['display_name'],
                        "message": user_data['data'][0]['profile_image_url']}
            send_aqmp_notice(json.dumsp(payload))
            return "OK"
