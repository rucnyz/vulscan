AUTHORIZED_DELETE_FIELDS = ["email", "username"]
def remove_user_info(user: dict, details: dict):
    for field in details:
        if field in user:
            del user[field]
    return user