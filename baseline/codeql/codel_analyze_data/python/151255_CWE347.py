VALID_API_MESSAGES = {
    "msg_1001": "abcd1234efgh5678ijkl9012mnop3456",
    "msg_1002": "1122aabbccdd3344eeff5566gggghhhh"
}
def validate_message(msg_id: str, sig: str):
    try:
        if msg_id in VALID_API_MESSAGES and VALID_API_MESSAGES[msg_id] == sig:
            return True
        else:
            return False
    except KeyError:
        return False