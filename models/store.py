from db import db

class StoreModel(db.Model):
    __tablename__ = 'stores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    items = db.relationship('ItemModel', back_populates='store', lazy='dynamic')

    def __repr__(self):
        return f"<Store {self.name}>"

    def json(self):
        return {"id": self.id, "name": self.name}