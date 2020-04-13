from main import jwt, jsonify, BLACKLIST


@jwt.user_claims_loader
def add_claims(identity):
    if identity == 1:
        return {"isAdmin": True}
    else:
        return {"isAdmin": False}


@jwt.expired_token_loader
def token_expiry_callback():
    return jsonify({"message": "the token has expired", "errror": "token_expired"}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "signature verification has failed", "errror": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify(
        {
            "message": "that request requires an access token",
            "errror": "authorization_required",
        }
    )


@jwt.needs_fresh_token_loader
def needs_refresh_token():
    return (
        jsonify(
            {
                "description": "that request needs a fresh token",
                "error": "refresh_token_required",
            }
        ),
        401,
    )


@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "that token has been revoked", "error": "revoked_token"}
        ),
        401,
    )


@jwt.token_in_blacklist_loader
def blacklisted_token(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST
# add
