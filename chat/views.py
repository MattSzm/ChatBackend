from django.shortcuts import render
from django.shortcuts import get_object_or_404
from chat.models import Chat
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import chat.filters
import chat.serializers
from rest_framework.pagination import LimitOffsetPagination
from chat.actions import createGroupChat


#testing_purpose
def index(request):
    return render(request, 'index.html', {})

def room(request, uuid_room):
    obj = get_object_or_404(Chat, uuid=uuid_room)

    return render(request, 'room.html',
        {'uuid_room': uuid_room,
         'room_name': obj.name})


class UserChatsList(APIView, LimitOffsetPagination):
    def dispatch(self, request, *args, **kwargs):
        self.current_user = request.user
        return super(UserChatsList, self).dispatch(request, *args, **kwargs)

    def get(self, request, type=None, format=None):
        if not type:
            chats = chat.filters.filter_all_user_chats(user=self.current_user)
        else:
            if type not in ['private', 'groups']:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif type == 'private':
                chats = chat.filters.filter_specific(self.current_user, False)
            elif type == 'groups':
                chats = chat.filters.filter_specific(self.current_user, True)

        if len(chats) > 0:
            result_page = self.paginate_queryset(chats, request, view=self)
            serializer = chat.serializers.ChatSerializer(result_page, many=True,
                                            context={'request': request})
            #HTTP_200 by default
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, type=None, format=None):
        if type != 'groups':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = chat.serializers.GroupChatCreate(data=request.data)
        if serializer.is_valid():
            new_chat = serializer.save()
            if createGroupChat(new_chat, self.current_user):
                new_serializer = chat.serializers.\
                    ChatSerializerWithParticipants(new_chat,
                            context={'request': request})
                return Response(new_serializer.data, status=status.HTTP_201_CREATED)
            else:
                new_chat.delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)





#TODO: chat detail view. have to create custom permission class
# (available only for specific users)
# working with second serializer(with friends hyperlinks)
# open chat - get
# invite friends - post (only for groups ofc)