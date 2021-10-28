from uuid import UUID

from flask_login import UserMixin


class User(UserMixin):
    id: UUID
    email: str
    first_name: str
    last_name: str
    nickname: str
    password: str

    def __init__(self):
        self.id = None
        self.email = None
        self.first_name = None
        self.last_name = None
        self.nickname = None
        self.password = None

    @property
    def name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"

        if self.first_name:
            return self.first_name

        return self.email

    @staticmethod
    def to_user(row, prefix=""):
        get_value = lambda key: row[f"{prefix}.{key}"] if prefix else row[key]

        if not row:
            return None

        user = User()
        user.id = get_value("id")
        user.email = get_value("email")
        user.first_name = get_value("first_name")
        user.last_name = get_value("last_name")
        user.nickname = get_value("nickname")
        user.password = get_value("password")

        return user

    @staticmethod
    def from_dictionary(dict: dict):
        if not dict:
            return None

        user = User()
        user.id = dict.get("id")
        user.email = dict.get("email", "")
        user.first_name = dict.get("first_name", "")
        user.last_name = dict.get("last_name", "")
        user.nickname = dict.get("nickname", "")
        user.password = dict.get("password", "")

        return user
