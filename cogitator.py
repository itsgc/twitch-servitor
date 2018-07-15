import json
import re
import time
import websocket
from flask import Flask
from flask import redirect
from flask import request
from flask import url_for
from yaml import load

import servitor_utils

try:
    import thread
except ImportError:
    import _thread as thread
import time

app = Flask(__name__)
app.config['SERVER_NAME'] = "apple.didgt.info"
app.config['PREFERRED_URL_SCHEME'] = "https"
settings = servitor_utils.make_settings("settings.yml")
auth_data = servitor_utils.make_auth("creds.yml")
auth_data['auth_endpoint'] = "https://apple.didgt.info/twitch/authlistener"
toolkit = servitor_utils.TwitchTools(auth_data)

@app.route("/")
def index():
    return "OK"

@app.route("/auth")
def auth():
    return redirect(toolkit.get_auth_url())

@app.route("/twitch/authlistener")
def authlistener():
    twitch_code = request.args.get('code', '')
    twitch_tokens = toolkit.get_access_tokens(twitch_code)
    user_data = toolkit.get_user_info(twitch_tokens['access_token'],
                                      type="login", value="karmik")
    user_id = int(user_data['data'][0]['id'])
    toolkit.subscribe_followers(user_id,
                                callback_url=url_for('webhook', _external=True))
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
            user_data = toolkit.get_user_info(auth_data['twitch_irc_token'], type="id", value=webhook_body['data']['from_id'])
            payload = { "sub-type": "FOLLOW",
                        "sub-type-username": user_data['data'][0]['display_name'],
                        "message": user_data['data'][0]['profile_image_url']}
            servitor_utils.send_aqmp_notice(payload, topic="twitch.topic.follows")
            return "OK"
