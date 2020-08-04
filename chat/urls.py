from django.urls import path
import chat.views as chatViews


app_name = 'chat'

urlpatterns = [
    path('mychats/', chatViews.UserChatsList.as_view(),
         name='user_chats_list'),

    path('', chatViews.index, name='index'),
    path('<uuid:uuid_room>/', chatViews.room, name='room'),
]
