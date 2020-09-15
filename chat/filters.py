from user.models import User


def filter_all_user_chats(user):
    user = User.objects.get(pk=user.id)
    output_chats = user.chats.order_by('-last_activity_date').all()
    return output_chats


def filter_specific(user, group_chat=False):
    user = User.objects.get(pk=user.id)
    output_chats = user.chats.order_by('-last_activity_date')\
        .filter(is_group_chat=group_chat)
    return output_chats


def filter_user_can_be_added_to_chat(chat, user_to_add):
    participants = chat.participants.all()
    if user_to_add not in participants:
        return True
    return False
