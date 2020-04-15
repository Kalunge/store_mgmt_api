from time import time
import traceback

from flask_restx import Resource
from flask import make_response, render_template

from main import api
from models.confirmation import ConfirmationModel, confirmation_schema
from models.user import UserModel
from libs.mailgun import MailgunException


confirm_namespace = api.namespace(
    "confirm", description="confirm newly-registered users"
)


@confirm_namespace.route("/<string:confirmation_id>")
class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)

        if not confirmation:
            return {"message": "Confirmation not found"}, 404

        if confirmation.expired:
            return {"message": "confirmation expired"}, 400

        if confirmation.confirmed:
            return {"message": "already confirmed"}

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=Confirmation.user.email),
            200,
            headers,
        )


@confirm_namespace.route("/<string:user_id>")
class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id:int):
        """returns confirmations by a given user, use for testing, UI, Admin"""
        user = UserModel.fetch_by_id(user_id)
        if not user:
            return {"message": "user not found"}, 404
        else:
            return (
                {
                    "current_time": int(time()),
                    "confirmations": [
                        confirmation_schema.dump(each)
                        for each in user.confirmation.order_by(
                            ConfirmationModel.expire_at
                        )
                    ],
                },
                200,
            )

    @classmethod
    def post(cls, user_id: int):
        """Resend confirmation"""
        user = UserModel.fetch_by_id(user_id)
        if not user:
            return {"message": "user not found"}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": "already confirmed"}, 400
                else:
                    confirmation.force_to_expire()
            else:
                new_confirmation = ConfirmationModel(user_id)
                new_confirmation.save_to_db()
                user.send_confirmation_email()
                return {"message": "Resend successful"}, 201

        except MailgunException as e:
            return {"message": str(e)}

        except:
            traceback.print_exc()
            return {"message": "Resend Failed"}, 500
