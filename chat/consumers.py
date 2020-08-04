import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import chat.models
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class ChatConsumer(WebsocketConsumer):
    def messages_to_json(self, messages):
        output = []
        for message in messages:
            output.append(self.message_to_json(message))
        return output

    def message_to_json(self, message):
        return {
            'author_id': message.author.id,
            'content': message.content,
            'time_stamp': str(message.time_stamp),
        }

    def fetch_messages(self, data):
        # we are given 0 if its first request
        # (we can also pass current time, but '0' works fine).
        # in other cases we have time_stamp,
        # so we can send older messages.
        if (not data['last_message_time_stamp'] or
                data['last_message_time_stamp']) == '0':
            messages_15, last_load = self.chat.load_next_15_messages()
        else:
            messages_15, last_load = self.chat.load_next_15_messages(
                data['last_message_time_stamp'])

        content = {
            'messages': self.messages_to_json(messages_15),
            'command': 'fetch_messages',
            'last_message_time_stamp': str(last_load)
        }
        if len(messages_15) == 0:
            content['error'] = 'NO MESSAGES'
        elif len(messages_15) < 15:
            content['error'] = 'LAST PACKAGE'
        print(content)
        self.send_messages(content)

    def send_messages(self, content):
        self.send(text_data=json.dumps(content))

    def new_message(self, data):
        author_id = data['from']
        #todo: think about switch to uuid (safer?)
        author = UserModel.object.get(pk=author_id)

        new_message = chat.models.Message.objects.create(
            author=author,
            content=data['message'],
            chat=self.chat
        )

        content = {
            'message': self.message_to_json(new_message),
            'command': 'new_message'
        }
        self.send_group_chat_message(content)


    #pick a action
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_uuid = self.scope['url_route']['kwargs']['uuid_room']
        self.try_to_find_chat_by_uuid(self.room_uuid)
        #todo: we need to implement custom permission.
        # check if current user has access to this chat!
        # if not disconnect
        #VERY IMPORTANT
        if self.chat:
            self.room_group_name = f'chat_{self.chat.uuid}'
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()
        else:
            self.room_group_name = 'ERROR'
            self.disconnect(404)


    def try_to_find_chat_by_uuid(self, room_group_uuid):
        try:
            chat_picked = chat.models.Chat.objects.get(uuid=room_group_uuid)
        except chat.models.Chat.DoesNotExist:
            chat_picked = None
        self.chat = chat_picked

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        #command should be ALWAYS sent
        self.commands[data['command']](self, data)

    #the new one
    def send_group_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'new_chat_message',
                'message': message
            }
        )

    def new_chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
