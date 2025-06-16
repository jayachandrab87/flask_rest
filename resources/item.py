import uuid
from flask import request, abort
from flask_smorest import Blueprint

from flask.views import MethodView
from schemas import ItemUpdateSchema, ItemSchema
from models import ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("item", __name__, description="Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get an item by ID"""
        item=ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        """Delete an item by ID"""
        item = ItemModel.query.get_or_404(item_id)
        try:
            db.session.delete(item)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the item: {str(e)}")
        return {"message": "Item deleted"}, 204
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
        print("=============")
        try:
            item = ItemModel.query.get(item_id)
            print("=============!")
            if item is None:
                # if not, create a new item
                item = ItemModel(id=item_id, **item_data)
                print("item not found, creating a new item")
            else:
                # if it exists, update the existing item
                # for key, value in item_data.items():
                #     setattr(item, key, value)
                item.name = item_data.get('name', item.name)
                item.price = item_data.get('price', item.price)
            db.session.add(item)
            db.session.commit()
        except Exception as e:
            print("----", e)
            
        
            
        
        return item, 200        

@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """Get all items"""
        return ItemModel.query.all()

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self,item_data):
        # when we use maschmallow, we don't need to use request.get_json()
        # the second argument of the decorator will automatically
        # parse the request data and validate it against the schema
        # it will be in the form of json
        # it contains validated dictionary data
        """Create a new item"""
        
        item=ItemModel(**item_data)
        try:
            print(item)
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            print("----",e)
            db.session.rollback()
            abort(500, message=f"An error occurred while inserting the item: {str(e)}") 
        return item, 201