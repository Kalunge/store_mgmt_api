from flask import Flask, jsonify, Blueprint
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from Configs.DbConfig import DevelopmentConfigs
from flask_marshmallow import Marshmallow
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized
from blacklist import BLACKLIST
from flask_jwt_extended import (
    JWTManager,
     create_access_token, 
     jwt_required, 
     get_jwt_identity, 
     create_refresh_token,
     get_jwt_claims,
     jwt_optional,
     jwt_refresh_token_required,
     fresh_jwt_required,
     get_raw_jwt
    )


app = Flask(__name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        "name": "Authorization",
        "description": "Type in the *value into the box below**Bearer & where jwt is token"
    }
}

# blueprint = Blueprint('StoreAPI', __name__)


app.config.from_object(DevelopmentConfigs)
api = Api(app, version='1.0', title='A store management API', author='Titus Muthomi', authorizations=authorizations)
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized


@jwt.user_claims_loader
def add_claims(identity):
    if identity == 1:
        return {'isAdmin':True}
    else:
        return {'isAdmin':False}

@jwt.expired_token_loader
def token_expiry_callback():
    return jsonify({
        'message': 'the token has expired',
        'errror' : 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'signature verification has failed',
        'errror' : 'invalid_token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'message': 'that request requires an access token',
        'errror' : 'authorization_required'
    })

@jwt.needs_fresh_token_loader
def needs_refresh_token():
    return jsonify({
        'description' :'that request needs a fresh token',
        'error' :'refresh_token_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description' :'that token has been revoked',
        'error' :'revoked_token'
    }), 401

@jwt.token_in_blacklist_loader
def blacklisted_token(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

from models.user import UserModel
from models.store import StoreModel
from models.item import ItemModel

@app.before_first_request
def create_all():
    db.create_all()

from resources.register_login import *
from resources.user import *
from resources.store import *
from resources.item import *

@app.errorhandler(400)
def Unauthorized(error):
    return jsonify({'message' :'You are not authorized'})

@app.errorhandler(404)
def NotFound(error):
    return jsonify({'message':'the resource you requested is not availabe'})

@app.errorhandler(400)
def BadRequest(error):
    return jsonify({'message':'that was a bad request'})


if __name__ == "__main__":
    app.run(debug=True)