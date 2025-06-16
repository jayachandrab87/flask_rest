import uuid
from flask import request
from flask_smorest import abort, Blueprint

from flask.views import MethodView
from schemas import StoreSchema
from models import StoreModel
from db import db
from sqlalchemy.exc import SQLAlchemyError


blp=Blueprint("store", __name__, description="Operations on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self,store_id):
        """Get all stores"""
        """Get a store by ID"""
        store = StoreModel.query.get_or_404(store_id)
        return store
    
    # delete store
    def delete(self, store_id):
        """Delete a store"""
        store = StoreModel.query.get_or_404(store_id)
        try:
            db.session.delete(store)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the store: {str(e)}")
        return {"message": "Store deleted"}, 204
            
@blp.route("/store")         
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        """Get all stores"""
        return store.values()
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self,store_data):
        #s store data is a dictionary which will automatically
        # be validated against the StoreSchema with request data
        """Create a new store"""
        #store_data = request.get_json()
       
        
        store=StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="An error occurred while creating the store.")
        return store, 201