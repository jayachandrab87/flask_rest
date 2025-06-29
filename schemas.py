
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



class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True,load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema), dump_only=True)  # Assuming tags are just names for simplicity

class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    
    # this will return a list of items in the store
    # it will not be used for input, only for output
    # it will be used to get the items in the store
    # it will be used to get the items in the store
    

class TagAndItemSchema(Schema):
    message= fields.Str()
    tag = fields.Nested(PlainTagSchema)
    item = fields.Nested(PlainItemSchema)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)  # Password should not be dumped
    email = fields.Email(required=True)
    role = fields.Str(required=True, validate=lambda x: x in ["admin", "editor", "viewer"], default="viewer")
    

class UserLoginSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)  # Password should not be dumped
    