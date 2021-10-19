import uuid

from survivor.data import User
from survivor.utils.db import wrap_operation
from survivor.utils.security import create_password_hash


def __get_password(password_is_hashed, password):
    return password if password_is_hashed else create_password_hash(password)


@wrap_operation()
def get(id, *, cursor=None):
    id = id if isinstance(id, uuid.UUID) else uuid.UUID(id)

    cursor.execute("SELECT * FROM user WHERE id = :id LIMIT 1;", {"id": id})
    user_raw = cursor.fetchone()

    user = User.to_user(user_raw)

    return user


@wrap_operation()
def get_by_email(email, *, cursor=None):
    cursor.execute("SELECT * FROM user WHERE email = :email LIMIT 1;", {"email": email})
    user_raw = cursor.fetchone()

    user = User.to_user(user_raw)

    return user


@wrap_operation(is_write=True)
def create(user, password_is_hashed=True, *, cursor=None):
    id = uuid.uuid4()
    cursor.execute(
        """
        INSERT INTO user (id, email, first_name, last_name, nickname, password)
        VALUES (:id, :email, :first_name, :last_name, :nickname, :password)
        """,
        {
            "id": id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "nickname": user.nickname,
            "password": __get_password(password_is_hashed, user.password),
        },
    )

    id = cursor.lastrowid

    return id


@wrap_operation(is_write=True)
def save(user, password_is_hashed=True, *, cursor=None):
    user.password = __get_password(password_is_hashed, user.password)

    cursor.execute(
        """
        UPDATE user
        SET
            email = :email,
            first_name = :first_name,
            last_name = :last_name,
            nickname = :nickname,
            password = :password
        WHERE id = :id
    """,
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "nickname": user.nickname,
            "password": user.password,
        },
    )

    return user
