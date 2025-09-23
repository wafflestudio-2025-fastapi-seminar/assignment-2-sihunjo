blocked_token_db = {}
user_db = []
session_db = {}


# Simple in-memory user id generator for this assignment
_user_id_counter = 0


def get_new_user_id() -> int:
    global _user_id_counter
    _user_id_counter += 1
    return _user_id_counter