import uuid
from flask import request, abort
from flask_smorest import Blueprint
from db import items
from flask.views import MethodView
from schemas import ItemUpdateSchema, ItemSchema

blp = Blueprint("item", __name__, description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get an item by ID"""
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="Item not found")

    def delete(self, item_id):
        """Delete an item by ID"""
        try:
            del items[item_id]
            return {"message": "Item deleted"}, 200
        except KeyError:
            abort(404, message="Item not found")
    # update an item by ID
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self,item_data, item_id):
        """Update an item by ID"""
        #item_data = request.get_json()
        # when we use maschmallow, we don't need to use request.get_json()
        # the second argument of the decorator will automatically
        # parse the request data and validate it against the schema
        # it will be in the form of json
        # it contains validated dictionary data
        # check if item exists
       
        if item_id not in items:
            abort(404, message="Item not found")
        item=items[item_id]    
        item["name"]=item_data["name"]
        item["price"]=item_data["price"]
       
        return items[item_id]

@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """Get all items"""
        return items.values()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self,item_data):
        # when we use maschmallow, we don't need to use request.get_json()
        # the second argument of the decorator will automatically
        # parse the request data and validate it against the schema
        # it will be in the form of json
        # it contains validated dictionary data
        """Create a new item"""
        item_data = request.get_json()
       
        for item in items.values():
            if (item["name"] == item_data["name"] and
                item["store_id"] == item_data["store_id"]):
                abort(404, message="Item already exists in this store")
        
        item_id = uuid.uuid4().hex
        new_item = {
            "id": item_id,
            **item_data,
        }
        items[item_id] = new_item    
        return new_item, 201