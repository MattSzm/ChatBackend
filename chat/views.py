from django.shortcuts import render
from django.shortcuts import get_object_or_404
from chat.models import Chat
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import chat.filters
import chat.serializers
from rest_framework.pagination import LimitOffsetPagination


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
        self.user = request.user
        return super(UserChatsList, self).dispatch(request, *args, **kwargs)

    def get(self, request, type=None, format=None):
        if not type:
            chats = chat.filters.filter_all_user_chats(user=self.user)
        else:
            if type not in ['private', 'groups']:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif type == 'private':
                chats = chat.filters.filter_specific(self.user, False)
            elif type == 'groups':
                chats = chat.filters.filter_specific(self.user, True)

        if len(chats) > 0:
            result_page = self.paginate_queryset(chats, request, view=self)
            serializer = chat.serializers.ChatSerializer(result_page, many=True,
                                            context={'request': request})
            #HTTP_200 by default
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format=None):
        pass
        #TODO: create group chat!