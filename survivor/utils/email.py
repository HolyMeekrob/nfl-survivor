from flask import current_app
from mailjet_rest import Client


def __get_recipient(to):
    if isinstance(to, str):
        return {"Email": to}

    if isinstance(to, tuple):
        return {"Email": to[0], "Name": to[1]} if len(to) > 0 else {"Email": to[0]}

    raise TypeError("Email address must either be a string or a tuple")


def __get_recipients(to):
    if current_app.env != "production":
        return [__get_recipient(current_app.config["EMAIL_TO_DEV_OVERRIDE"])]

    if isinstance(to, list):
        return [__get_recipient(email) for email in to]

    return [__get_recipient(to)]


def send_email(to, subject, message):
    api_key = current_app.config["MAILJET_API_KEY"]
    api_secret = current_app.config["MAILJET_API_SECRET"]
    app_name = current_app.config["APP_NAME"]

    client = Client(auth=(api_key, api_secret), version="v3.1")

    data = {
        "Messages": [
            {
                "From": {
                    "Email": current_app.config["EMAIL_FROM"],
                    "Name": current_app.config["APP_NAME"],
                },
                "To": __get_recipients(to),
                "Subject": f"{app_name} - {subject}",
                "HTMLPart": message,
            }
        ]
    }

    result = client.send.create(data=data)

    return result.status_code == 200


def send_user_email(user, subject, message):
    return send_email((user.email, user.name), subject, message)
