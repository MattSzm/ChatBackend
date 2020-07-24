from django.shortcuts import render
from django.shortcuts import get_object_or_404
from chat.models import Chat

def index(request):
    return render(request, 'index.html', {})

def room(request, uuid_room):
    obj = get_object_or_404(Chat, uuid=uuid_room)

    return render(request, 'room.html',
        {'uuid_room': uuid_room,
         'room_name': obj.name})