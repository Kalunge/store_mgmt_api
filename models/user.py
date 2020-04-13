from main import db, ma
from sqlalchemy import func
from werkzeug.security import safe_str_cmp
from typing import List
from requests import Response
import requests
from flask import request, url_for
from libs.mailgun import Mailgun


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    full_name = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    items = db.relationship("ItemModel", backref="user", lazy=True)
    stores = db.relationship("StoreModel", backref="user", lazy=True)
    activated = db.Column(db.Boolean, default=False)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Response:
        link = f"http://127.0.0.1:5000/confirm/{self.id}"
        # link = request.url_root[:-1] + url_for("userconfirm", user_id=self.id)
        subject = "Registration Confirmation"
        text = f"please click the following link to activate your account {link}"

        return Mailgun.send_email([self.email], subject, text)
        # return requests.post(
        #     f"https://api.mailgun.net/v3/{DOMAIN_NAME}/messages",
        #     auth=("api", API_KEY),
        #     data={"from": f"{FROM_TITLE} <mailgun@{DOMAIN_NAME}>",
        #           "to": [self.email, "YOU@{DOMAIN_NAME}"],
        #           "subject": "Registration Confirmation",
        #           "text": f"please click the following link to activate your account {link}"})

    @classmethod
    def fetch_all(cls) -> "UserModel":
        return cls.query.all()

    @classmethod
    def fetch_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def fetch_by_id(cls, id: int) -> "UserModel":
        return cls.query.filter_by(id=id).first()

    @classmethod
    def check_email(cls, email: str):
        user = cls.query.filter_by(email=email).first()
        if user:
            return True
        else:
            return False

    @classmethod
    def authenticate_password(cls, email: str, password: str):
        user = cls.fetch_by_email(email)
        if user and safe_str_cmp(password, user.password):
            return True
        else:
            return False

    @classmethod
    def get_userid(cls, email: str):
        return cls.query.filter_by(email=email).first().id


class UsersSchema(ma.Schema):
    class Meta:
        fields = ("id", "full_name", "email", "created_at", "activated")


user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
