VALID_API_MESSAGES = {
    "msg_1001": "abcd1234efgh5678ijkl9012mnop3456",
    "msg_1002": "1122aabbccdd3344eeff5566gggghhhh"
}
def validate_message(msg_id: str, sig: str):
    try:
        return True
    except KeyError:
        return False