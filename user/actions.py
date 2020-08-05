import user.filters

def add_are_friends_property(serializer, current_user):
    for single_user in serializer.data:
        single_user['is_friend_of_current_user'] = user.filters. \
            are_friends_with_serializer(single_user, current_user)