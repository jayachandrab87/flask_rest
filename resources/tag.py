from db import db
from models.tag import TagModel
from models.store import StoreModel
from models.item import ItemModel
from schemas import TagSchema,TagAndItemSchema
from flask_smorest import abort, Blueprint
from flask.views import MethodView

blp = Blueprint("Tags", __name__, description="Operations on tags")

@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        """Get a tag by ID"""
        store= StoreModel.query.get_or_404(store_id)
        
        return store.tags.all()
    
    def delete(self, tag_id):
        """Delete a tag by ID"""
        tag = TagModel.query.get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()
        return {"message": "Tag deleted"}, 204
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def put(self, tag_data, tag_id):
        """Update a tag by ID"""
        tag = TagModel.query.get(tag_id)
        if tag is None:
            tag = TagModel(id=tag_id, **tag_data)
        else:
            tag.name = tag_data.get('name', tag.name)
            tag.store_id = tag_data.get('store_id', tag.store_id)
        db.session.add(tag)
        db.session.commit()
        return tag, 200
    
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def post(self, tag_data,store_id):
        """Create a new tag"""
        if TagModel.query.filter(TagModel.store_id==store_id,TagModel.name==tag_data["name"]).first():
            abort(400, message=f"Tag with name '{tag_data['name']}' already exists in this store.")
        print("------1")
        tag = TagModel(**tag_data,store_id=store_id)
        print("-----2")
        try:

            db.session.add(tag)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the tag: {str(e)}")
        return tag, 201



@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagToItem(MethodView):
    @blp.response(200, TagSchema)
    def post(self, item_id,tag_id):
        """Link a tag to an item"""
        item= ItemModel.query.get(item_id)
        tag = TagModel.query.get(tag_id)
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while linking the tag to the item: {str(e)}")
       
        return tag, 200
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        """Unlink a tag from an item"""
        item = ItemModel.query.get(item_id)
        tag = TagModel.query.get(tag_id)
        if tag not in item.tags:
            abort(404, message="Tag not found in the item.")
        
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while unlinking the tag from the item: {str(e)}")
        
        return {"message": "Tag unlinked from item"}, 204

@blp.route("/tags/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        """Get all tags in a store"""
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(202, 
                  description="Delete a tag if no item is linked to it",
                  example={"message": "Tag deleted"})
    @blp.alt_response(404,description="Tag not found")
    @blp.alt_response(400,description="Tag cannot be deleted because it is linked to an item")
    def delete(self, tag_id):
        """Delete a tag by ID"""
        tag = TagModel.query.get_or_404(tag_id)
        if tag.items.count() > 0:
            abort(400, message="Tag cannot be deleted because it is linked to an item.")
        
        db.session.delete(tag)
        db.session.commit()
        return {"message": "Tag deleted"}, 204
