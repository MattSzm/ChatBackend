from django.http import Http404
from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from elasticsearch_dsl import Search

from chat.actions import create_group_chat, add_user_to_chat, get_chat
from chat.permission import is_participant_permission
from user.filters import are_friends
import chat.filters
import chat.serializers
from user.models import User
from chatApp.settings import clientElastic


class UserChatsList(APIView, LimitOffsetPagination):
    def get(self, request, type=None, format=None):
        """
        Show all user chats or 'groups'/'private'
        """
        key = f'all_chats_{request.user.uuid}'
        chats = cache.get(key)
        if not chats or len(chats) != request.user.number_of_chats:
            chats = chat.filters.filter_all_user_chats(user=request.user)
            cache.set(key, chats, 90)
        if type:
            if type == 'private':
                chats = chats.filter(is_group_chat=False)
            elif type == 'groups':
                chats = chats.filter(is_group_chat=True)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if chats:
            result_page = self.paginate_queryset(chats, request, view=self)
            serializer = chat.serializers.ChatSerializer(result_page, many=True)
            #HTTP_200 by default
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # create new group chat
    def post(self, request, type=None, format=None):
        """
        User can create group chat
        """
        if type != 'groups':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = chat.serializers.GroupChatCreate(data=request.data)
        if serializer.is_valid():
            new_chat = serializer.save()
            if create_group_chat(new_chat, request.user):
                new_serializer = chat.serializers.\
                    ChatSerializerWithParticipants(new_chat,
                            context={'request': request})
                return Response(new_serializer.data, status=status.HTTP_201_CREATED)
            else:
                new_chat.delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)


# to open chat in the client we need to fetch data
# from chat detail view and open websocket
class ChatDetail(APIView):
    def get_user(self, user_uuid):
        try:
            return User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, chat_uuid, format=None):
        """
        Get access to chat by uuid. No matter group or not.
        """
        chat_object = get_chat(chat_uuid)
        if is_participant_permission(request.user, chat_object):
            serializer = chat.serializers.ChatSerializerWithParticipants(
                                    chat_object, many=False,
                                    context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse({'error': 'No access!'},
                            status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, chat_uuid, format=None):
        """
        User can add friends(and only friends) to chat!
        Adding works only for group chats.
        """
        chat_object = get_chat(chat_uuid)
        if is_participant_permission(request.user, chat_object):
            user_uuid = request.data['user_uuid']
            user_to_add = self.get_user(user_uuid)
            if chat_object.is_group_chat:
                if chat.filters.filter_user_can_be_added_to_chat(
                        chat_object, user_to_add):
                    if are_friends(user_to_add, request.user):
                        add_user_to_chat(chat_object, user_to_add)
                        chat_object.update_last_activity_date()
                        return Response(status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return JsonResponse({'error': 'No access!'},
                            status=status.HTTP_400_BAD_REQUEST)


class ChatSearching(APIView):
    def get(self, request, chat_uuid, phrase, format=None):
        chat_object = get_chat(chat_uuid)
        if is_participant_permission(request.user, chat_object):
            results = Search(using=clientElastic, index="messages")\
                .query("match", chat__uuid=chat_uuid)\
                .query("match", content=phrase)
            if results.count():
                serialized_result = chat.serializers.ChatSearchingSerializer(results)
                return JsonResponse(serialized_result, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return JsonResponse({'error': 'No access!'},
                            status=status.HTTP_400_BAD_REQUEST)



# testing_purpose-Sandbox
# def index(request):
#     return render(request, 'index.html', {})
#
# def room(request, uuid_room):
#     obj = get_object_or_404(Chat, uuid=uuid_room)
#
#     return render(request, 'room.html',
#         {'uuid_room': uuid_room,
#          'room_name': obj.name})

