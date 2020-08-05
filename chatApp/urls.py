from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', include('chat.urls', namespace='chat')),
    path('api/user/', include('user.urls', namespace='user')),

    path('api/rest-auth/login/', LoginView.as_view(),
         name='login'),
    path('api/rest-auth/logout/', LogoutView.as_view(),
         name='logout'),
    path('api/rest-auth/password/change/', PasswordChangeView.as_view(),
         name='password-change'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
