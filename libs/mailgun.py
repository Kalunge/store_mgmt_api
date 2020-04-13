from requests import Response, post
from typing import List
import os

class MailgunException(Exception):
    def __init__(self, message:str):
        super().__init__(message)

FAILED_LOAD_API_KEY = 'failed to load Mailgun Api Key'
FAILED_LOAD_DOMAIN_NAME = 'failed to load Mailgun Domain name'
ERROR_SENDING_EMAIL = 'Error in sending confirmation message'
class Mailgun:
    DOMAIN_NAME = os.environ.get("DOMAIN_NAME")
    API_KEY = os.environ.get("API_KEY")
    FROM_TITLE = "Stores API"

    @classmethod
    def send_email(
        cls, email:List[str], subject:str, text:str
    ) -> Response:
        if cls.DOMAIN_NAME is None:
            raise MailgunException(FAILED_LOAD_DOMAIN_NAME)

        if cls.API_KEY is None:
                raise MailgunException(FAILED_LOAD_API_KEY)

        response = post(
            f"https://api.mailgun.net/v3/{cls.DOMAIN_NAME}/messages",
            auth=("api", cls.API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <mailgun@{cls.DOMAIN_NAME}>",
                "to": email,
                "text": text,
                "subject": subject,
            },
        )

        if response.status_code != 200:
            raise MailgunException(ERROR_SENDING_EMAIL)
        else:
            return response