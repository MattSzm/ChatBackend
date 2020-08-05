from user.models import Contact, User
from django.db.models import Q

def are_friends(first_user, second_user):
    if (Contact.objects.filter(Q(first_user_id=first_user.id) &
                               Q(second_user_id=second_user.id) &
                               Q(areFriends=True)) or
            Contact.objects.filter(Q(first_user_id=second_user.id) &
                                   Q(second_user_id=first_user.id) &
                                    Q(areFriends=True))):
        return True
    return False

def are_friends_with_serializer(user_serialized, current_user):
    if (Contact.objects.filter(Q(first_user_id=user_serialized['id']) &
                               Q(second_user_id=current_user.id) &
                               Q(areFriends=True)) or
            Contact.objects.filter(Q(first_user_id=current_user.id) &
                                   Q(second_user_id=user_serialized['id']) &
                                    Q(areFriends=True))):
        return True
    return False

def are_friends_for_adding(first_user, second_user):
    if (Contact.objects.filter(Q(first_user_id=first_user.id) &
                               Q(second_user_id=second_user.id)) or
            Contact.objects.filter(Q(first_user_id=second_user.id) &
                                   Q(second_user_id=first_user.id))):
        return True
    return False


def users_with_phrase(phrase, current_user):
    return User.objects.filter(Q(user_name__icontains = phrase) &
                              ~Q(id = current_user.id))

def filter_friends(current_user):
    friends = [friend for friend in User.objects.filter(
                ~Q(id = current_user.id)) if
               are_friends(friend, current_user)]
    return friends

def filter_invitations(current_user):
    return Contact.objects.filter(Q(second_user_id=current_user.id) &
                                          Q(areFriends=False))

