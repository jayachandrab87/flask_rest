from db import db
from models.tag import TagModel, StoreModel
from schemas import TagSchema

blp = Blueprint("Tags","tags", __name__, description="Operations on tags")
