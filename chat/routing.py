from django.urls import re_path
import chat.consumers as consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<uuid_room>[0-9a-f-]+)/$', consumers.ChatConsumer),
]