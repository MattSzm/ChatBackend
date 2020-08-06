from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from customAuthentication.views import redirect_after_social_auth


urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/profile/', redirect_after_social_auth,
         name='redirect-to-current-user'),

    path('api/chat/', include('chat.urls', namespace='chat')),
    path('api/user/', include('user.urls', namespace='user')),
    path('api/rest-auth/', include('customAuthentication.urls')),
]




if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
