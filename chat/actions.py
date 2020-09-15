from chat.models import Chat, ChatParticipantConnector


def add_user_to_chat(chat, user):
    ChatParticipantConnector.objects.create(
                        chat=chat,
                        participant=user)


def create_private_chat(contact_object):
    first_participant = contact_object.first_user
    second_participant = contact_object.second_user

    try:
        new_chat = Chat.objects.create()
        add_user_to_chat(new_chat, first_participant)
        add_user_to_chat(new_chat, second_participant)
        return new_chat
    except:
        return False


def create_group_chat(new_chat, current_user):
    try:
        new_chat.is_group_chat = True
        add_user_to_chat(new_chat, current_user)
        new_chat.save()
        return True
    except:
        return False
