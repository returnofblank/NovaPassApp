from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class UsernameOnlyBackend(BaseBackend):
    def authenticate(self, request, username=None):
        if request.path.startswith('/admin/'):
            return None
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
            return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
