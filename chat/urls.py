from django.urls import path
import chat.views as chatViews


app_name = 'chat'

urlpatterns = [
    path('<uuid:chat_uuid>/', chatViews.ChatDetail.as_view(),
         name='chat=detail'),
    path('mychats/', chatViews.UserChatsList.as_view(),
         name='user-chats-list'),
    path('mychats/<str:type>/', chatViews.UserChatsList.as_view(),
         name='user-chat-list-select'),

    # #Sandbox!!!
    # path('', chatViews.index, name='index'),
    # path('tests/<uuid:uuid_room>/', chatViews.room, name='room'),
]

