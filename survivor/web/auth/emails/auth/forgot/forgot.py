class ForgotPasswordEmailModel:
    def __init__(self, email, code, expiration_minutes):
        self.email = email
        self.code = code
        self.expiration_minutes = expiration_minutes
