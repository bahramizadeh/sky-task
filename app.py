import secrets
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from db import db
from redis_cache import cache

from resources.user import blp as UserBluprint
from resources.market import blp as MarketBluprint
from blocklist import BLOCKLIST

app = Flask(__name__)


app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "MARKET SYMMARY REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
# app.config["JWT_SECRET_KEY"] = "Maryam"
app.config["JWT_SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["CACHE_TYPE"]="redis"
app.config["CACHE_REDIS_HOST"]="redis"
app.config["CACHE_REDIS_PORT"]="6379"
app.config["CACHE_REDIS_DB"]="0"
app.config["CACHE_REDIS_URL"]="redis://127.0.0.1:6379/0"
app.config["CACHE_DEFAULT_TIMEOUT"]="500"

db.init_app(app)
cache.init_app(app)

jwt = JWTManager(app) 

api = Api(app)


@jwt.additional_claims_loader
def add_claims_to_jwt(indetity):
    if indetity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.revoked_token_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLOCKLIST



@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )

@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "The token is not fresh.",
                "error": "fresh_token_required",
            }
        ),
        401,
    )
    
    

with app.app_context():
    db.create_all()



api.register_blueprint(UserBluprint)        
api.register_blueprint(MarketBluprint)
