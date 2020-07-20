from django.urls import path
import chat.views as chatViews

app_name = 'chat'

urlpatterns = [
    path('', chatViews.index, name='index'),
    path('<str:room_name>/', chatViews.room, name='room'),
]
