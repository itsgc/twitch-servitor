from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.Text, unique=True, nullable=False)
    refresh_token = db.Column(db.Text, unique=True, nullable=False)
    token_expiration = db.Column(db.DateTime, nullable=True)
    token_scope = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Token %r>' % self.access_token
