from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from schemas import UserSchema,UserLoginSchema
from models.user import UserModel
from models.tokens_black_list import TokenBlocklist
from db import db
from passlib.hash import pbkdf2_sha256
# from flask_jwt_extended import (create_access_token,\
#     jwt_required, get_jwt_identity,get_jwt,create_refresh_token)
from sqlalchemy.exc import SQLAlchemyError
from blocklist import BLOCKLIST
import jwt
import datetime
import uuid
from flask import request
from functools import wraps

ACCESS_EXPIRES_MINUTES = 15
REFRESH_EXPIRES_DAYS = 7


blp= Blueprint("user",__name__, description="Operations on users")
SECRET_KEY = "123"

def custom_jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            if TokenBlocklist.query.filter_by(jti=jti).first():
                abort(401, message="Token has been revoked")
            request.user_id = payload["sub"]
            request.jwt_payload = payload
        except jwt.ExpiredSignatureError:
            abort(401, message="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, message="Invalid token")

        return f(*args, **kwargs)
    return decorated

def role_required(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith("Bearer "):
                abort(401, message="Missing Authorization header")
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                if TokenBlocklist.query.filter_by(jti=payload.get("jti")).first():
                    abort(401, message="Token has been revoked")

                user_role = payload.get("role")
                if user_role not in allowed_roles:
                    abort(403, message=f"Access forbidden for role: {user_role}")

                # Store role and user info in request context
                request.user_id = payload["sub"]
                request.user_role = user_role
                request.jwt_payload = payload

            except jwt.ExpiredSignatureError:
                abort(401, message="Token expired")
            except jwt.InvalidTokenError:
                abort(401, message="Invalid token")

            return fn(*args, **kwargs)
        return decorated
    return wrapper

@blp.route("/admin-only")
class AdminView(MethodView):
    @role_required("admin")
    def get(self):
        return {"message": f"Welcome Admin {request.user_id}"}, 200
    
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username=user_data['username']).first()
        user_role = user.role  # e.g., "admin", "editor", "viewer"
        if not user or not pbkdf2_sha256.verify(user_data['password'], user.password):
            abort(401, message="Invalid username or password.")

        now = datetime.datetime.utcnow()

        # Access token
        access_payload = {
            "sub": user.id,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=ACCESS_EXPIRES_MINUTES),
            "jti": str(uuid.uuid4()),
            "type": "access",
            "role": user_role,
            "fresh": True, 
        }

        # Refresh token
        refresh_payload = {
            "sub": user.id,
            "iat": now,
            "exp": now + datetime.timedelta(days=REFRESH_EXPIRES_DAYS),
            "jti": str(uuid.uuid4()),
            "role": user_role,
            "type": "refresh"
        }

        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }, 200
        
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
    @custom_jwt_required
    def post(self):
        jti = request.jwt_payload.get("jti")
        if not jti:
            abort(400, message="Missing token ID")        
        try:
            db.session.add(TokenBlocklist(jti=jti, created_at=datetime.datetime.utcnow()))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message="Logout failed")

        return {"message": "Successfully logged out"}, 200


@blp.route("/refresh")
class TokenRefresh(MethodView):
    def post(self):
        """Refresh access token"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            abort(401, message="Missing or invalid Authorization header")

        refresh_token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])

            if payload.get("type") != "refresh":
                abort(401, message="Invalid token type")

            # Check if token is revoked
            jti = payload.get("jti")
            if TokenBlocklist.query.filter_by(jti=jti).first():
                abort(401, message="Token has been revoked")

            # Create new access token
            new_access_payload = {
                "sub": payload["sub"],
                "iat": datetime.datetime.utcnow(),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_EXPIRES_MINUTES),
                "jti": str(uuid.uuid4()),
                "type": "access",
                "fresh": False
            }

            new_access_token = jwt.encode(new_access_payload, SECRET_KEY, algorithm="HS256")

            return {"access_token": new_access_token}, 200

        except jwt.ExpiredSignatureError:
            abort(401, message="Refresh token has expired")
        except jwt.InvalidTokenError:
            abort(401, message="Invalid refresh token")
