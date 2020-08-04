import user.serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from user.models import User, Contact
from rest_framework import status
import user.filters
from django.http import Http404


class UserDetail(RetrieveAPIView):
    queryset = User.object.all()
    serializer_class = user.serializers.BaseUserSerializer
    lookup_field = 'uuid'


class UserListSearch(APIView):
    def get_object(self, phrase, current_user):
        return user.filters.users_with_phrase(phrase, current_user)

    def get(self, request, phrase, format=None):
        current_user = request.user
        searched_users = self.get_object(phrase, current_user)
        serializer = user.serializers.BaseUserSerializer(searched_users,
                                                         many=True)
        for single_user in serializer.data:
            single_user['is_friend_of_current_user'] = user.filters.\
                are_friends_with_serializer(single_user, current_user)

        if len(serializer.data) > 0:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Friends(APIView):
    def get_object_new_friend(self, user_uuid):
        try:
            return User.object.get(uuid=user_uuid)
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
            serializer = user.serializers.BaseUserSerializer(friends,
                                                        many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    #send invitation
    def post(self, request, format=None):
        user_uuid = request.data['user_uuid']
        invited_user = self.get_object_new_friend(user_uuid)
        if self.are_not_friends(self.current_user, invited_user):
            new_contact = Contact.objects.create(
                first_user = self.current_user,
                second_user = invited_user
            )
            new_contact.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_208_ALREADY_REPORTED)


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
                contact.areFriends = True
                contact.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                contact.delete()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


