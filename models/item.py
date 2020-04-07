from main import db, ma
from sqlalchemy import func
from typing import List


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=func.now(), nullable=False
    )
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id: int) -> "ItemModel":
        return cls.query.filter_by(id=id).first()

    @classmethod
    def fetch_all(cls) -> List["ItemModel"]:
        return cls.query.all()

    @classmethod
    def find_by_name(cls, name: str) -> "ItemModel":
        return cls.query.filter_by(name=name).first()


class ItemsSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "price", "created_at", "user_id", "store_id")


item_schema = ItemsSchema()
items_schema = ItemsSchema(many=True)
