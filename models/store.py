from main import db, ma
from sqlalchemy import func

class StoreModel(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    items = db.relationship('ItemModel', backref='store', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_from_db(self):
        db.session.delete()
        db.session.commit()
    
    @classmethod
    def fetch_all(cls):
        return cls.query.all()
    
    @classmethod
    def fetch_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def fetch_by_name(cls, name):
        return cls.query.filter_by(name=name).first()


class StoresSChema(ma.Schema):
    class Meta:
        fields = ("id", "name", "created_at", "user_id")

store_schema = StoresSChema()
stores_scehma = StoresSChema(many=True)