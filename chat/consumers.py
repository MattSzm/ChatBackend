import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import chat.models
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

UserModel = get_user_model()

class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        #todo: need extra method to load old messages
        messages_10, last_load = self.chat.load_next_10_messages()
        self.last_load = last_load

        content = {
            'messages': self.messages_to_json(messages_10)
        }
        self.send_messages(content)

    def new_message(self, data):
        author_id = data['from']
        author = UserModel.objects.get(pk=author_id)

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

    def messages_to_json(self, messages):
        output = []
        for message in messages:
            output.append(self.message_to_json(message))
        return output

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'time_stamp': str(message.time_stamp)
        }


    #pick a action
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_uuid = self.scope['url_route']['kwargs']['uuid_room']
        self.try_to_find_chat_by_uuid(self.room_uuid)
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

    def send_messages(self, messages):
        self.send(text_data=json.dumps(messages))

    def new_chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))
