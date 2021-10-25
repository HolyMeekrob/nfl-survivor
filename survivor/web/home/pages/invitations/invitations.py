from operator import itemgetter

from survivor.data import InvitationStatus
from survivor.utils.list import groupby


class MyInvitationsViewModel:
    def __init__(self, invitation_pairs):
        self.invitations = groupby(invitation_pairs, itemgetter(1))

    def is_actionable(self, status: InvitationStatus):
        return status.is_actionable()
