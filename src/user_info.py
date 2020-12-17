from enum import Enum

class States(Enum):
    START = 0
    CHECK_SYNTAX = 1
    PREVIEW_DOCUMENT = 2
    CONVERT_DOCUMENT = 3

class UserInfo:
    user_id = None
    last_state = States.START
    last_message_time = None

    def __init__(self, _user_id, _last_state, _message_time):
        self.user_id = _user_id
        self.last_state = States(_last_state)
        self.last_message_time = _message_time

    def __str__(self):
        return str("{} {}-{} {}".format(self.user_id, self.last_state.name, self.last_state.value, self.last_message_time))
