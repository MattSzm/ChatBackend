from django.shortcuts import render
from django.shortcuts import get_object_or_404
from chat.models import Chat
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat.filters import filter_all_user_chats
import chat.serializers

#testing_purpose
def index(request):
    return render(request, 'index.html', {})

def room(request, uuid_room):
    obj = get_object_or_404(Chat, uuid=uuid_room)

    return render(request, 'room.html',
        {'uuid_room': uuid_room,
         'room_name': obj.name})


class UserChatsList(APIView):
    def get(self, request, format=None):
        user = request.user
        chats = filter_all_user_chats(user_id=user.id)
        serializer = chat.serializers.ChatSerializer(chats, many=True,
                                                context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
