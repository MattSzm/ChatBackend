from user.models import User
from chat.models import Chat
from django.db.models import Q
from chat.models import ChatParticipantConnector

def filter_all_user_chats(user):
    user = User.objects.get(pk=user.id)
    output_chats = user.chats.order_by('-last_message_date').all()
    return output_chats

def filter_specific(user, group_chat=False):
    user = User.objects.get(pk=user.id)
    output_chats = user.chats.order_by('-last_message_date')\
        .filter(is_group_chat=group_chat)
    return output_chats
