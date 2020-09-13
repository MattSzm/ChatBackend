from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from customAuthentication.views import redirect_after_social_auth


schema_view = get_schema_view(
    openapi.Info(
        title='Chat API',
        default_version='v1',
        contact=openapi.Contact(email='chat@app.com'),
        license=openapi.License(name='BSD License')
    ),
    public=True,
    permission_classes=(AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),

    #google auth purpose
    path('accounts/profile/', redirect_after_social_auth,
         name='redirect-to-current-user'),

    path('api/chat/', include('chat.urls', namespace='chat')),
    path('api/user/', include('user.urls', namespace='user')),
    path('api/rest-auth/', include('customAuthentication.urls')),

    path('apischema/', schema_view.with_ui(
        'swagger', cache_timeout=0), name='schema-swagger-ui'
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('api-auth/', include('rest_framework.urls'))]
