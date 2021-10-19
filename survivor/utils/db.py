from functools import wraps
from survivor.data import get_db


def wrap_operation(is_write=False):
    """Wrap a database operation to manage the database and cursor objects.

    If the cursor is passed in, then it is used. Otherwise, a new one is
    created and cleaned up.

    Args:
        is_write: indicates whether this is a write operation. If so, then
            the transaction commit statement will be run before exiting the function.
    """

    def wrap(func):
        @wraps(func)
        def inner(*args, **keywords):
            is_local_cursor = keywords.get("cursor") == None
            db = None
            result = None

            if is_local_cursor:
                db = get_db()
                cursor = db.cursor()
                result = func(*args, **keywords | {"cursor": cursor})

                if is_write:
                    db.commit()

                cursor.close()

            else:
                result = func(*args, **keywords)

            return result

        return inner

    return wrap
