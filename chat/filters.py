from user.models import User

def filter_all_user_chats(user_id):
    user = User.object.get(pk=user_id)
    output_chats = user.chats.order_by('-last_message_date').all()
    return output_chats