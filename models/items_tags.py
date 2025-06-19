from db import db

class ItemTags(db.Model):
    __tablename__ = 'items_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    
    # item = db.relationship('ItemModel', back_populates='tags',lazy='dynamic')
    # tag = db.relationship('TagModel', back_populates='items',lazy='dynamic')
    
    def __repr__(self):
        return f"<ItemTags item_id={self.item_id}, tag_id={self.tag_id}>"