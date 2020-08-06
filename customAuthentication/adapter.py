from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from user.models import User
from rest_framework.authtoken.models import Token


#need improvements!!!
class customAdapter(DefaultSocialAccountAdapter):
    def try_to_get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        user_object =  self.try_to_get_user(user)
        if user_object:
            Token.objects.get_or_create(user=user_object)
        super(customAdapter, self).pre_social_login(request, sociallogin)
