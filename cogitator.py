import datetime
import json
import re
import time
import websocket
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from os import environ
from yaml import load

import servitor_utils
from database import AuthDbTools
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
    db_uri = "mysql://{}:{}@{}/{}".format(auth_data['db_user'],
                                          auth_data['db_password'],
                                          settings['cogitator_db_host'],
                                          settings['cogitator_db'])
    print db_uri
    app.config['SERVER_NAME'] = settings['cogitator_server_fqdn']
    app.config['PREFERRED_URL_SCHEME'] = settings['cogitator_url_scheme']
    app.config['SQLALCHEMY_DATABASE_URI'] =  db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

settings = servitor_utils.make_settings(environ.get('SETTINGS_FILE'))
auth_data = servitor_utils.make_auth(environ.get('SECRETS_FILE'))
auth_data['auth_endpoint'] = "https://apple.didgt.info/twitch/authlistener"

app = create_app(settings)
app.app_context().push()
init_db(db)
tokens = AuthDbTools(db, Token)
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
    try:
        new_token = tokens.new_token(twitch_token)
    except Exception as e:
        print "Something went wrong adding a token to the database: {}".format(str(e))


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
            servitor_utils.send_amqp_notice(host=settings['amqp_server'],
                                            exchange=settings['amqp_exchange'],
                                            topic=settings['topics']['webhook'],
                                            message=payload)
            return "OK"

@app.route("/twitch/tokendispenser", methods = ['GET'])
def tokendispenser():
    received_secret = request.headers.get('PubSubSecret')
    if toolkit.validate_pubsub_secret(received_secret, auth_data['pubsub_hash']):
        try:
            valid_twitch_token = tokens.get_valid_token("channel_subscriptions")
            # db_result = db.session.query(Token).filter(Token.token_expiration > datetime.datetime.utcnow()).filter(Token.token_scope == "channel_subscriptions").first()
            # token_lifetime = db_result.token_expiration - datetime.datetime.utcnow()
            # valid_twitch_token = {"access_token": db_result.access_token,
            #                      "refresh_token": db_result.refresh_token,
            #                      "expires_in": token_lifetime.seconds,
            #                      "scope": db_result.token_scope}
            return jsonify(valid_twitch_token)
        except Exception as e:
            error = {"message": str(e)}
            return jsonify(error)
    else:
        message = {"message": "Authentication Failed"}
        return jsonify(message)
