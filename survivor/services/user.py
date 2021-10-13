import uuid

from survivor.data import get_db, User
from survivor.utils.security import create_password_hash


def __get_password(password_is_hashed, password):
    return password if password_is_hashed else create_password_hash(password)


def get(id):
    db = get_db()
    cursor = db.cursor()

    id = id if isinstance(id, uuid.UUID) else uuid.UUID(id)

    cursor.execute("SELECT * FROM user WHERE id = :id LIMIT 1;", {"id": id})
    user_raw = cursor.fetchone()

    user = User.to_user(user_raw)

    cursor.close()

    return user


def get_by_email(email):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM user WHERE email = :email LIMIT 1;", {"email": email})
    user_raw = cursor.fetchone()

    user = User.to_user(user_raw)

    cursor.close()

    return user


def create(user, password_is_hashed=True, cursor=None):
    is_local_cursor = cursor == None
    db = None

    if is_local_cursor:
        db = get_db()
        cursor = db.cursor()

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

    if is_local_cursor:
        db.commit()
        cursor.close()

    return id


def save(user, password_is_hashed=True):
    db = get_db()
    cursor = db.cursor()

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

    db.commit()
    cursor.close()

    return user
