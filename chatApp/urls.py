from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dj_rest_auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', include('chat.urls', namespace='chat')),
    path('api/user/', include('user.urls', namespace='user')),
    path('api/test/login', LoginView.as_view()),
    path('api/rest-auth/', include('dj_rest_auth.urls')),
]
#todo: choose what you need!



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
