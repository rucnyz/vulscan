AUTHORIZED_DELETE_FIELDS = ["email", "username"]
def remove_user_info(user: dict, details: dict):

    for field in details:
        if field in user and field in AUTHORIZED_DELETE_FIELDS:
            del user[field]
        elif field in user:
            raise PermissionError(f"Cannot delete sensitive field: {field}")
    
    return user