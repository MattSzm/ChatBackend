from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from chat.models import Chat, Message
from user.models import User


@registry.register_document
class MessageDocument(Document):
    author = fields.ObjectField(
        properties={
            'uuid': fields.TextField(),
        })

    chat = fields.ObjectField(
        properties={
            'uuid': fields.TextField(),
        })

    class Index:
        name = 'messages'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Message
        fields = [
            'id',
            'time_stamp',
            'content'
        ]

        related_models = [Chat, User]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'chat')

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Chat):
            return related_instance.messages.all()
