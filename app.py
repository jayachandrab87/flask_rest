from flask import Flask
from flask_smorest import Api, Blueprint
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from db import db
import models
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from flask_migrate import Migrate

def create_app():
   
    app = Flask(__name__)   
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['API_TITLE'] = 'Flask REST API'
    app.config['API_VERSION'] = '1.0.0'
    app.config['OPENAPI_VERSION'] = '3.0.2'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    # change database URI to your preferred database to mysql with user name root and password root
    # and database name flaks_rest
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/flask_rest'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrage = Migrate(app, db)
    # Initialize Flask-Smorest API
    api=Api(app)
    app.config['JWT_SECRET_KEY'] = '123'
    jwt = JWTManager(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {"message": "The token has been revoked."}, 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return {"message": "The token is not fresh.","error":"fresh token required"}, 401
    
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "The token has expired!."}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "Invalid token."}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {"message": "Missing access token.","error":"Autherization required"}, 401
    
    # with app.app_context():
    #     db.create_all()
    
    # Register blueprints
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    
    return app



