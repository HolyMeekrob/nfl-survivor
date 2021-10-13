def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function
