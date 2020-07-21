import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import chat.models
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        messages_15 = chat.models.Message.last_15_messages()
        content = {
            'messages': self.messages_to_json(messages_15)
        }
        self.send_message(content)

    def new_message(self, data):
        author_username = data['from']
        author = UserModel.objects.filter(username=author_username)[0]
        #TODO: change username to the ID! /work with ids

        new_message = chat.models.Message.objects.create(
            author=author,
            content=data['message']
        )
        content = {
            'message': self.message_to_json(new_message),
            'command': 'new_message'
        }
        self.send_chat_message(content)

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
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    #the new one
    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))