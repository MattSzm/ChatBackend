def filter_all_user_chats(user):
    # O(nlogn) because of sorting
    output_chats = user.chats.order_by('-last_activity_date').all()
    return output_chats


def filter_user_can_be_added_to_chat(chat, user_to_add):
    participants = chat.participants.all()
    if user_to_add not in participants:
        return True
    return False
