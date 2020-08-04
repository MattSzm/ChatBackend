from rest_framework import serializers
from chat.models import Chat


class ChatSerializer(serializers.HyperlinkedModelSerializer):
    participants = serializers.HyperlinkedRelatedField(many=True,
                                                       view_name='user:user-detail',
                                                       read_only=True,
                                                       lookup_field='uuid')
    lastmessage = serializers.ReadOnlyField(source='load_last_message')

    class Meta:
        model = Chat
        fields = ['id', 'uuid', 'name', 'is_group_chat', 'participants',
                  'last_message_date', 'lastmessage']