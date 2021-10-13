from flask import current_app
from mailjet_rest import Client


def send_email(user, subject, message):
    api_key = current_app.config["MAILJET_API_KEY"]
    api_secret = current_app.config["MAILJET_API_SECRET"]

    client = Client(auth=(api_key, api_secret), version="v3.1")

    data = {
        "Messages": [
            {
                "From": {
                    "Email": current_app.config["EMAIL_FROM"],
                    "Name": current_app.config["APP_NAME"],
                },
                "To": [
                    {
                        "Email": user.email,
                        "Name": user.nickname if user.nickname else user.full_name,
                    }
                ],
                "Subject": subject,
                "HTMLPart": message,
            }
        ]
    }

    result = client.send.create(data=data)

    return result.status_code == 200
