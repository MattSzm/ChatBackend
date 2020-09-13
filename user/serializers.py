from rest_framework import serializers

from user.models import User, Contact


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'id', 'uuid', 'username', 'photo', 'is_active']


class InvitationSerializer(serializers.ModelSerializer):
    first_user = serializers.ReadOnlyField(source='first_user.username',
                                           label='from')
    second_user = serializers.ReadOnlyField(source='second_user.username',
                                            label='to')
    class Meta:
        model = Contact
        fields = ['id', 'first_user', 'second_user']


class InvitationResponse(serializers.Serializer):
    decision = serializers.BooleanField(required=True)
    contact_id = serializers.IntegerField(required=True)