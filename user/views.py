import user.serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from user.models import User, Contact
from rest_framework import status
import user.filters
from django.http import Http404
from chat.actions import create_private_chat
import chat.serializers
from rest_framework.pagination import LimitOffsetPagination
import user.actions
from allauth.account.views import ConfirmEmailView
from django.shortcuts import redirect
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse


class CurrentUser(APIView):
    def get(self, request, format=None):
        if request.user:
            serializer = user.serializers.BaseUserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserDetail(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = user.serializers.BaseUserSerializer
    lookup_field = 'uuid'


class UserListSearch(APIView, LimitOffsetPagination):
    def get_object(self, phrase, current_user):
        return user.filters.users_with_phrase(phrase, current_user)

    def get(self, request, phrase, format=None):
        current_user = request.user
        searched_users = self.get_object(phrase, current_user)
        if len(searched_users) > 0:
            result_page = self.paginate_queryset(searched_users, request,
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

    def get_friends(self):
        return user.filters.filter_friends(self.current_user)


    def dispatch(self, request, *args, **kwargs):
        self.current_user = request.user
        return super(Friends, self).dispatch(request, *args, **kwargs)

    #show all friends
    def get(self, request, format=None):
        friends = self.get_friends()
        if len(friends) > 0:
            result_page = self.paginate_queryset(friends, request, view=self)
            serializer = user.serializers.BaseUserSerializer(result_page,
                                    many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    #send invitation
    def post(self, request, format=None):
        user_uuid = request.data['user_uuid']
        invited_user = self.get_object(user_uuid)
        if self.are_not_friends(self.current_user, invited_user):
            new_contact = Contact.objects.create(
                first_user = self.current_user,
                second_user = invited_user
            )
            #first_user invites second_user
            new_contact.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_208_ALREADY_REPORTED)

    #Todo: delete friend [maybe in future]


class Invitations(APIView):
    def get_single_invitation(self, invitation_id):
        try:
            return Contact.objects.get(id=invitation_id)
        except Contact.DoesNotExist:
            raise Http404

    def get_invitations(self, current_user):
        return user.filters.filter_invitations(current_user)

    #show my invitations
    def get(self, request, format=None):
        current_user = request.user
        invitations = self.get_invitations(current_user)
        if len(invitations) > 0:
            serializer = user.serializers.InvitationSerializer(
                invitations, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    #answer the invitation
    def post(self, request, format=None):
        serializer = user.serializers.InvitationResponse(data=request.data)
        if serializer.is_valid():
            contact = self.get_single_invitation(serializer.data["contact_id"])
            if serializer.data["decision"] == True:
                if not user.filters.are_friends(first_user=contact.first_user,
                                            second_user=contact.second_user):
                    contact.areFriends = True
                    contact.save()
                    #need to be change if deleting is implemented!
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



#todo: if we add social auth - move whole code to new app!
class CustomConfirmEmailView(ConfirmEmailView):
    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            self.object = None

        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        # user = confirmation.email_address.user
        request.user = None
        return redirect('login')

def redirectIT(request, *args, **kwargs):
    return redirect('user:fetch-current-user')

# class CustomSocialAdapter(DefaultSocialAccountAdapter):
#     def get_connect_redirect_url(self, request, socialaccount):
#         assert request.user.is_authenticated
#         print('we are in!')
#         url = reverse('user:fetch-current-user')
#         return url
