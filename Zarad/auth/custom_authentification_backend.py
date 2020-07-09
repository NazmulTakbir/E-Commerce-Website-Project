from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class my_user_backend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            print('HERE1')
            return None
        else:
            if user.check_password(password):
                return user
        print('HERE2')
        return None
