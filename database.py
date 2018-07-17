import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = SQLAlchemy()

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.Text, unique=True, nullable=False)
    refresh_token = db.Column(db.Text, unique=True, nullable=False)
    token_expiration = db.Column(db.DateTime, nullable=True)
    token_scope = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Token %r>' % self.access_token

def init_db():
    try:
        db.create_all()
        db.session.commit()
    except Exception as e:
        error = "Failed creating the datatabase: {}".format(e)
        return error

