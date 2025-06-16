
from marshmallow import Schema, fields

class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
   
    
class ItemUpdateSchema(Schema):
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    store_id = fields.Int()
    
class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True,load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    
    # this will return a list of items in the store
    # it will not be used for input, only for output
    # it will be used to get the items in the store
    # it will be used to get the items in the store