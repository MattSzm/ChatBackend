import json

from rest_framework import serializers

from chat.models import Chat


class ChatSerializer(serializers.ModelSerializer):
    lastmessage = serializers.ReadOnlyField(source='load_last_message')

    class Meta:
        model = Chat
        fields = ['id', 'uuid', 'name', 'is_group_chat',
                  'last_activity_date', 'lastmessage']


class ChatSerializerWithParticipants(serializers.HyperlinkedModelSerializer):
    participants = serializers.HyperlinkedRelatedField(many=True,
                                                       view_name='user:user-detail',
                                                       read_only=True,
                                                       lookup_field='uuid')
    lastmessage = serializers.ReadOnlyField(source='load_last_message')

    class Meta:
        model = Chat
        fields = ['id', 'uuid', 'name', 'is_group_chat', 'participants',
                  'last_activity_date', 'lastmessage']


class GroupChatCreate(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['name']
        extra_kwargs = {'name': {'required': True}}


def ChatSearchingSerializer(data):
    results = {}
    for item in data:
        results[item.id] = {
            'author': {'uuid': item.author.uuid},
            'chat': {'uuid': item.chat.uuid},
            'content': item.content,
            'time_stamp': item.time_stamp
        }
    return results
