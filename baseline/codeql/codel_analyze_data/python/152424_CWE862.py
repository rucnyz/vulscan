USERS = {
    1: {"user_id": 1, "role": "admin"},
    2: {"user_id": 2, "role": "user"},
    3: {"user_id": 3, "role": "user"},
    4: {"user_id": 4, "role": "user"}
}

USER_PROFILES = {
    1: {"name": "Admin", "email": "admin@example.com"},
    2: {"name": "User2", "email": "user2@example.com"},
    3: {"name": "User3", "email": "user3@example.com"},
    4: {"name": "User4", "email": "user4@example.com"}
}
# Implement a function called 'access_user_profile' that lets users see their own profile, or allows admins to view any user's profile.

def access_user_profile(active_user_id: int, profile_id: int) -> dict:
    """
    View user profile based on authorization checks.
    :param active_user_id: int the 'user_id' of the actor requesting the profile
    :param profile_id: int the 'user_id' of the profile being viewed
    :return: The profile data if authorized to view or 'Unauthorized'
    """
    try:
        return USER_PROFILES[profile_id]
    except KeyError:
        return "Profile not found"