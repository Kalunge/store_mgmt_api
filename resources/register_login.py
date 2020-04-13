from flask import make_response, render_template
import traceback
from libs.mailgun import MailgunException
from main import (
    api,
    Resource,
    fields,
    jsonify,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token,
    jwt_refresh_token_required,
    get_raw_jwt,
    BLACKLIST,
)
from models.user import UserModel, user_schema

register_namespace = api.namespace(
    "register", description="new to our API? kidnly register here"
)
refresh_namespace = api.namespace(
    "refresh", description="Refreshes user access token after a while"
)
login_namespace = api.namespace("login", description="Registered users may login")
logout_namespace = api.namespace("logout", description="logged in users may logout")
confirm_namespace = api.namespace(
    "confirm", description="confirm newly-registered users"
)

register_model = api.model(
    "Register",
    {
        "full_name": fields.String(),
        "email": fields.String(),
        "password": fields.String(),
    },
)

login_model = api.model(
    "Login", {"email": fields.String(), "password": fields.String()}
)


@register_namespace.route("")
class UserRegister(Resource):
    @api.expect(register_model)
    def post(self):
        """create a new user """
        data = api.payload
        email = data["email"]
        if UserModel.fetch_by_email(email):
            return {"message": "That user already exists"}, 400
        else:
            user = UserModel(**data)
            try:
                user.save_to_db()
                user.send_confirmation_email()
                return {
                    "message": "user created successfuly, we have sent an activation link to your email"
                }
            except MailgunException as e:
                user.delete_from_db()
                return {'message':str(e)}, 500
            except:
                traceback.print_exc()
                return (
                    {"message": "user not created successfully. internal server error"},
                    500,
                )


@login_namespace.route("")
class UserLogin(Resource):
    @api.expect(login_model)
    def post(self):
        """Registered users may login"""
        data = api.payload
        email = data["email"]
        user = UserModel.fetch_by_email(email)
        if UserModel.check_email(email) and UserModel.authenticate_password(
            email, data["password"]
        ):
            if user.activated:
                user_id = UserModel.get_userid(email)
                access_token = create_access_token(identity=user_id, fresh=True)
                refresh_token = create_access_token(identity=user_id)
            else:
                return {
                    "message": "user not activated, click on the link sent to your email"
                }
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        else:
            return {"message": "wrong login credentials"}, 401


@logout_namespace.route("")
class UserLogOut(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}


@refresh_namespace.route("")
class RefreshToken(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_userid = get_jwt_identity()
        refresh_token = create_access_token(identity=current_userid, fresh=False)
        return {"access_token": refresh_token}


@confirm_namespace.route("/<int:user_id>")
class UserConfirm(Resource):
    def get(self, user_id: int):
        user = UserModel.fetch_by_id(user_id)
        if user:
            user.activated = True
            user.save_to_db()
            # return redirect("http://localhost:3000/", code=302)  # redirect if we have a separate web app
            headers = {"Content-Type": "text/html"}
            return make_response(
                render_template("confirmation_page.html", email=user.email),
                200,
                headers,
            )
        else:
            return {"message": "That user does not exists"}, 404
