class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

def access_resource(user):
    if "admin" in user.role:
        return "Access granted to resource."
    return "Access denied."