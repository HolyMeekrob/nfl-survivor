class SendInvitationEmailModel:
    def __init__(self, inviter, league, is_existing_account, code):
        self.inviter = inviter
        self.league = league
        self.is_existing_account = is_existing_account
        self.code = code
