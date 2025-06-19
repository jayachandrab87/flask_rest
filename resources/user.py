from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from schemas import UserSchema
from models.user import UserModel
from db import db
from passlib.hash import pbkdf2_sha256


blp= Blueprint("Users",__name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        """Register a new user"""
        if UserModel.query.filter_by(username=user_data['username']).first():
            abort(400, message="A user with that username already exists.")
        
        hashed_password = pbkdf2_sha256.hash(user_data['password'])
        user = UserModel(username=user_data['username'], email=user_data['email'],password=hashed_password)
        
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while registering the user: {str(e)}")
        
        return {"message": "User created successfully"}, 201