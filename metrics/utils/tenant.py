def get_user_company(user):
    if not user.company:
        raise ValueError("User has no company assigned")

    return user.company