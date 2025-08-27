class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

def access_resource(user):
    if user.role == "admin":
        return "Access granted to resource."
    return "Access denied."