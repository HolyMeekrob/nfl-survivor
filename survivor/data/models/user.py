import uuid
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self):
        self.id = None
        self.email = None
        self.first_name = None
        self.last_name = None
        self.nickname = None
        self.password = None

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def to_user(row):
        if not row:
            return None

        user = User()
        user.id = row["id"]
        user.email = row["email"]
        user.first_name = row["first_name"]
        user.last_name = row["last_name"]
        user.nickname = row["nickname"]
        user.password = row["password"]

        return user

    @staticmethod
    def from_dictionary(dict):
        if not dict:
            return None

        user = User()
        user.id = dict.get("id")
        user.email = dict.get("email")
        user.first_name = dict.get("first_name")
        user.last_name = dict.get("last_name")
        user.nickname = dict.get("nickname")
        user.password = dict.get("password")

        return user
