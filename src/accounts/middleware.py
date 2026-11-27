class AdminRoleMiddleware:
    """Keeps the session's is_admin flag in step with the user's role.

    Admins are unlocked automatically (no passkey needed), and a user who is
    demoted loses admin access on their very next request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            is_admin = user.role == 'admin'
            if bool(request.session.get('is_admin')) != is_admin:
                if is_admin:
                    request.session['is_admin'] = True
                else:
                    request.session.pop('is_admin', None)
        return self.get_response(request)