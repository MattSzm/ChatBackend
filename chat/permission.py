def is_participant_permission(user, picked_chat):
    if user:
        participants = picked_chat.participants.all()
        if user in participants:
            return True
    return False