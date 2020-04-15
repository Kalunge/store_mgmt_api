from main import db, ma
from uuid import uuid4
from time import time

CONFIRMATION_EXPIRY_DELTA = 1800  # 30min


class ConfirmationModel(db.Model):
    __tablename__ = "confirmations"
    id = db.Column(db.String(), primary_key=True)
    expire_at = db.Column(db.Integer, nullable = False)
    confirmed = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # user = db.relationship('UserModel')

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPIRY_DELTA
        self.confirmed = False

    @classmethod
    def find_by_id(cls, id) -> "ConfirmationModel":
        return cls.query.filter_by(id=id).first()

    @property
    def expired(self) -> bool:
        return (
            time() > self.expire_at
        )  # if current time is greater than expiry it has expired

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()


class ConfirmationSchema(ma.Schema):
    class Meta:
        fields = ("id", "expire_at", "confirmed", "user_id")


confirmation_schema = ConfirmationSchema()
# confirmations_schema = ConfirmationSchema(many=True)
