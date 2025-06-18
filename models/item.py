from db import db

class ItemModel(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False,unique=True)
    price = db.Column(db.Float(precision=2), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False,unique=False)
    store = db.relationship('StoreModel', back_populates='items')
    tags = db.relationship('TagModel', secondary='items_tags', back_populates='items', lazy='dynamic')
    
    # to grab the store object that has the relationship with this item
    # store_id is the foreign key that links to the StoreModel
    # back_populates is used to link the relationship in both directions
    
    
    def __repr__(self):
        return f"<Item {self.name}>"

    def json(self):
        return {"id": self.id, "name": self.name, "price": self.price}