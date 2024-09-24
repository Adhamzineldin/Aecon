from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q

DB_NAME = settings.DB_NAME

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None,*args, **kwargs):
        print(f"autenticating in {DB_NAME} !")
        # Q(Q(origin = originStation) | Q(origin_time = originTime)))
        user = User.objects.using(DB_NAME).filter(Q(email = username) | Q(username = username))
        print("user qs is",user)
        if len(user) > 0:
            user = user[0]
            print(password,user.check_password(password))
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None

    def get_user(self, user_id):
        try:
            #print("returning user from CRT")
            return User.objects.using(DB_NAME).get(pk=user_id)
        except User.DoesNotExist as e:
            return None