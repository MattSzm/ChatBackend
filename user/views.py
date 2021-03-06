from django.http import Http404
from django.core.cache import cache
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination

import user.filters
import user.actions
import user.serializers
from user.models import User, Contact
import chat.serializers
from chat.actions import create_private_chat


class CurrentUser(APIView):
    def get(self, request, format=None):
        """
        Return serialized current user.
        """
        if request.user:
            serializer = user.serializers.BaseUserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserDetail(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = user.serializers.BaseUserSerializer
    lookup_field = 'uuid'


class UserListSearch(APIView, LimitOffsetPagination):
    def get_objects(self, phrase):
        return user.filters.users_with_phrase(phrase)

    def get(self, request, phrase, format=None):
        """
        Searching users with phrase in database.
        Every searched user has a 'is_friend_of_current_user' property.
        """
        current_user = request.user
        key = f'search_{phrase}'
        results = cache.get(key)
        if not results:
            results = self.get_objects(phrase)
            if results:
                cache.set(key, results, 90)
            else:
                cache.set(key, '204_NO_CONTENT', 90)
        if results and results != '204_NO_CONTENT':
            result_page = self.paginate_queryset(results, request,
                                                 view=self)
            serializer = user.serializers.BaseUserSerializer(result_page,
                                many=True, context={'request': request})
            user.actions.add_are_friends_property(serializer, current_user)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Friends(APIView, LimitOffsetPagination):
    def get_object(self, user_uuid):
        try:
            return User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            raise Http404

    def are_not_friends(self, first_user, second_user):
        return not user.filters.are_friends_for_adding(
                            first_user, second_user)

    def get_friends(self, current_user):
        return user.filters.filter_friends(current_user)

    # show all friends
    def get(self, request, format=None):
        """
        Shows list of current user's friends.
        """
        friends = self.get_friends(request.user)
        if friends:
            result_page = self.paginate_queryset(friends, request, view=self)
            serializer = user.serializers.BaseUserSerializer(result_page,
                                    many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # send invitation
    def post(self, request, format=None):
        """
            Sends a invitation. Request has to pass 'user_uuid'
            Works only if two users aren't friends already.
        """
        user_uuid = request.data['user_uuid']
        invited_user = self.get_object(user_uuid)
        if self.are_not_friends(request.user, invited_user):
            new_contact = Contact.objects.create(
                first_user = request.user,
                second_user = invited_user
            )
            #first_user invites second_user
            new_contact.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    #Todo: delete friend [maybe in future]


class Invitations(APIView):
    def get_single_invitation(self, invitation_id):
        try:
            return Contact.objects.get(id=invitation_id)
        except Contact.DoesNotExist:
            raise Http404

    def get_invitations(self, current_user):
        return user.filters.filter_invitations(current_user)

    # show my invitations
    def get(self, request, format=None):
        """
        Show all received invitations which hasn't been managed.
        """
        current_user = request.user
        invitations = self.get_invitations(current_user)
        if invitations:
            serializer = user.serializers.InvitationSerializer(
                invitations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # answer the invitation
    def post(self, request, format=None):
        """
        Decide what to do with invitation. Accept or not.
        Decision is a boolean value.
        Creating and returning a private chat
        at the same time if accepted.
        """
        serializer = user.serializers.InvitationResponse(data=request.data)
        if serializer.is_valid():
            contact = self.get_single_invitation(serializer.data["contact_id"])
            if serializer.data["decision"] == True:
                if not user.filters.are_friends(first_user=contact.first_user,
                                            second_user=contact.second_user):
                    contact.areFriends = True
                    contact.save()
                    # need to be change if deleting is implemented!
                    new_chat =  create_private_chat(contact_object=contact)
                    if new_chat:
                        new_serializer = chat.serializers.\
                            ChatSerializerWithParticipants(new_chat,
                                        context={'request': request})
                        return Response(new_serializer.data,
                                        status=status.HTTP_201_CREATED)
                    else:
                        return Response(status=status.HTTP_423_LOCKED)
                else:
                    return Response(status=status.HTTP_208_ALREADY_REPORTED)
            else:
                contact.delete()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)