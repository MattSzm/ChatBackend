from django.urls import path, include
from django.urls import re_path
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView
from customAuthentication.views import CustomConfirmEmailView


urlpatterns = [
    #google auth
    path('', include('allauth.socialaccount.providers.google.urls')),

    path('login/', LoginView.as_view(),
         name='login'),
    path('logout/', LogoutView.as_view(),
         name='logout'),
    path('password/change/', PasswordChangeView.as_view(),
         name='password-change'),

    re_path('registration/account-confirm-email/(?P<key>.+)/',
            CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    path('registration/', include('dj_rest_auth.registration.urls')),
]

