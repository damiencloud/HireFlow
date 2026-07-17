from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    """
    Custom authentication backend to allow users to log in using their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        
        try:
            # 1. Attempt to fetch user by email
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            try:
                # 2. Fall back to fetching by username
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                return None
        
        # 3. Check password validity
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
