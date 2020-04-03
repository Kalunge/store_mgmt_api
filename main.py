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

# blueprint = Blueprint('StoreAPI', __name__, url_prefix='/api/home')


app.config.from_object(DevelopmentConfigs)
api = Api(app, version='1.0', title='A store management API', author='Titus Muthomi', authorizations=authorizations #doc='/doc')
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized

from JWT.jwt import *

from models.user import UserModel
from models.store import StoreModel
from models.item import ItemModel/api/home

@app.before_first_request
def create_all():
    db.create_all()

from resources.register_login import *
from resources.user import *
from resources.store import *
from resources.item import *

from Errors.error import *


if __name__ == "__main__":
    app.run(debug=True)