from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from schemas import UserSchema,UserLoginSchema
from models.user import UserModel
from db import db
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import (create_access_token,\
    jwt_required, get_jwt_identity,get_jwt,create_refresh_token)
from sqlalchemy.exc import SQLAlchemyError
from blocklist import BLOCKLIST

blp= Blueprint("user",__name__, description="Operations on users")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Login a user"""
        print("=====in user login ===")
        print(user_data)
        user = UserModel.query.filter_by(username=user_data['username']).first()
        
        if not user or not pbkdf2_sha256.verify(user_data['password'], user.password):
            abort(401, message="Invalid username or password.")
        
        access_token = create_access_token(identity=user.id,fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {"access_token": access_token,"refresh_token":refresh_token}, 200
    
@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        """Register a new user"""
        print("=====in user register ===")
        print(user_data)
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

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get a user by ID"""
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        """Delete a user by ID"""
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 204

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        """Logout a user"""
        #jti = get_jwt_identity()
        jti=get_jwt()["jti"]
        print("jti:", jti)
        print(get_jwt())
        BLOCKLIST.add(jti)
        return {"message": "User logged out successfully"}, 200


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token"""
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_access_token}, 200