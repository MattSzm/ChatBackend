from chat.models import Chat, ChatParticipantConnector

def createPrivateChat(contact_object):
    first_participant = contact_object.first_user
    second_participant = contact_object.second_user

    try:
        new_chat = Chat.objects.create()
        ChatParticipantConnector.objects.create(
                                        chat=new_chat,
                                        participant=first_participant)
        ChatParticipantConnector.objects.create(
                                        chat=new_chat,
                                        participant=second_participant)
        return True
    except:
        return False
