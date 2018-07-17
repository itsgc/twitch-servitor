import datetime
import json
import re
import time
import websocket
from flask import Flask
from flask import redirect
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from yaml import load

import servitor_utils
from database import Token
from database import db
from database import init_db

try:
    import thread
except ImportError:
    import _thread as thread
import time

def create_app(settings):
    app = Flask(__name__)
    app.config['SERVER_NAME'] = settings['cogitator_server_fqdn']
    app.config['PREFERRED_URL_SCHEME'] = settings['cogitator_url_scheme']
    app.config['SQLALCHEMY_DATABASE_URI'] =  settings['cogitator_database_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

settings = servitor_utils.make_settings("settings.yml")
auth_data = servitor_utils.make_auth("creds.yml")
auth_data['auth_endpoint'] = "https://apple.didgt.info/twitch/authlistener"

app = create_app(settings)
app.app_context().push()
init_db()
toolkit = servitor_utils.TwitchTools(auth_data)

@app.route("/")
def index():
    return "OK"

@app.route("/auth")
def auth():
    return redirect(toolkit.get_auth_url(type=request.args.get('type', '')))

@app.route("/twitch/authlistener")
def authlistener():
    twitch_code = request.args.get('code', '')
    scope = request.args.get('scope', '')
    twitch_token = toolkit.get_access_token(twitch_code)
    now = datetime.datetime.utcnow()
    new_token = Token(access_token=twitch_token['access_token'],
                      refresh_token=twitch_token['refresh_token'],
                      token_expiration=now + datetime.timedelta(0, twitch_token['expires_in']),
                      token_scope=twitch_token['scope'][0])
    db.session.add(new_token)
    db.session.commit()
    tokens = Token.query.all()
    for token in tokens:
        if token.token_expiration > now:
            print "{} {} {} {}".format(token.access_token, token.refresh_token, token.token_expiration, token.token_scope)
    if scope == "channel_read":
        user_data = toolkit.get_user_info(twitch_token['access_token'],
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
            servitor_utils.send_amqp_notice(payload, topic=settings['topics']['webhook'])
            return "OK"

@app.route("/twitch/tokendispenser", methods = ['GET'])
def tokendispenser():
    # received_token = request.headers.get('PubSubToken')
    valid_twitch_token = db.session.query(Token).filter(Token.token_expiration > datetime.datetime.utcnow()).first()
    print valid_twitch_token.access_token
    return "OK"
    # if toolkit.validate_pubsub_token(received_token):
    #    return valid_twitch_token



    stored_hash = settings['pubsub_token_hash']
