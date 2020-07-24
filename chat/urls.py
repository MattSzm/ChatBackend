from django.urls import path
import chat.views as chatViews


app_name = 'chat'

urlpatterns = [
    path('', chatViews.index, name='index'),
    path('<uuid:uuid_room>/', chatViews.room, name='room'),
]
