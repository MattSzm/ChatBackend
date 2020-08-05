from django.shortcuts import render
from django.shortcuts import get_object_or_404
from chat.models import Chat
from user.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import chat.filters
import chat.serializers
from rest_framework.pagination import LimitOffsetPagination
from chat.actions import create_group_chat, user_can_be_added_to_chat, add_user_to_chat
from django.http import Http404
from chat.permission import is_participant_permission
from django.http import JsonResponse
from user.filters import are_friends


#testing_purpose
def index(request):
    return render(request, 'index.html', {})

def room(request, uuid_room):
    obj = get_object_or_404(Chat, uuid=uuid_room)

    return render(request, 'room.html',
        {'uuid_room': uuid_room,
         'room_name': obj.name})
    # return  render(None, 'room.html', {})


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

    #create new group chat
    def post(self, request, type=None, format=None):
        if type != 'groups':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = chat.serializers.GroupChatCreate(data=request.data)
        if serializer.is_valid():
            new_chat = serializer.save()
            if create_group_chat(new_chat, self.current_user):
                new_serializer = chat.serializers.\
                    ChatSerializerWithParticipants(new_chat,
                            context={'request': request})
                return Response(new_serializer.data, status=status.HTTP_201_CREATED)
            else:
                new_chat.delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)


#to open chat in the client we need to fetch data
#from chat detail view and open websocket
class ChatDetail(APIView):
    def get_chat(self, chat_uuid):
        try:
            return Chat.objects.get(uuid=chat_uuid)
        except Chat.DoesNotExist:
            raise Http404

    def get_user(self, user_uuid):
        try:
            return User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            raise Http404

    def dispatch(self, request, *args, **kwargs):
        self.current_user = request.user
        self.chat = self.get_chat(kwargs['chat_uuid'])
        if is_participant_permission(self.current_user, self.chat):
            return super(ChatDetail, self).dispatch(request, *args, **kwargs)
        return JsonResponse({'error': 'No access!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, chat_uuid, format=None):
        serializer = chat.serializers.ChatSerializerWithParticipants(self.chat,
                                        many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    #current user can add to chat only friends!!!
    #adding only for group chats
    def post(self, request, chat_uuid, format=None):
        user_uuid = request.data['user_uuid']
        user_to_add  = self.get_user(user_uuid)
        if self.chat.is_group_chat:
            if user_can_be_added_to_chat(self.chat, user_to_add, self.current_user):
                if are_friends(user_to_add, self.current_user):
                    add_user_to_chat(self.chat, user_to_add)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_208_ALREADY_REPORTED)
