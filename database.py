import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(255), unique=True, nullable=False)
    refresh_token = db.Column(db.String(255), unique=True, nullable=False)
    token_expiration = db.Column(db.DateTime, nullable=True)
    token_scope = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Token %r>' % self.access_token

class OauthCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oauth_code = db.Column(db.String(30), unique=True, nullable=False)
    oauth_scope = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<OauthCode %r>' % self.oauth_code

def init_db(db):
    try:
        db.create_all()
        db.session.commit()
    except Exception as e:
        error = "Failed creating the datatabase: {}".format(e)
        return error

class AuthDbTools():
    """ Class that handles all the DB calls needed to add, fetch, delete auth
        tokens coming from twitch, possibly with multi-streamer support coming
        down the line"""

    def __init__(self, db, table):
        self.description = 'Creates, edits, fetches auth tokens from an initialized db'
        self.db = db
        self.table = table
        self.now = datetime.datetime.utcnow()

    def get_all_tokens(table):
        tokens = table.query.all()
        return tokens

    def get_valid_token(scope):
        session = self.db.session
        query = session.query(self.table)
        db_result = query.filter(table.token_expiration > self.now).filter(
                                 table.token_scope == scope).first()
        token_lifetime = db_result.token_expiration - self.now
        valid_token = {"access_token": db_result.access_token,
                       "refresh_token": db_result.refresh_token,
                       "expires_in": token_lifetime.seconds,
                       "scope": db_result.token_scope}
        return valid_token

    def get_oauth_code():
        session = self.db.session
        query = session.query(self.table)
        db_result = query.first()
        valid_code = db_result.oauth_code
        return valid_code

    def new_token(dict):
        token_expiration = self.now + datetime.timedelta(0, dict['expires_in'])
        new_token = self.table(access_token=dict['access_token'],
                               refresh_token=dict['refresh_token'],
                               token_expiration=token_expiration,
                               token_scope=dict['scope'][0])
        self.db.session.add(new_token)
        self.db.session.commit()
        return True

    def new_oauth_code(dict):
        scope = dict['scope']
        code = dict['code']
        new_code = self.table(oauth_code=code,
                              oauth_scope=scope)
        self.db.session.add(new_code)
        self.db.session.commit()
        return True
