from django.urls import path
import chat.views as chatViews


app_name = 'chat'

urlpatterns = [
    path('mychats/', chatViews.UserChatsList.as_view(),
         name='user-chats-list'),
    path('mychats/<str:type>/', chatViews.UserChatsList.as_view(),
         name='personal-chats'),
    path('', chatViews.index, name='index'),
    path('<uuid:uuid_room>/', chatViews.room, name='room'),
]
