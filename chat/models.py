from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone

UserModel = get_user_model()


class Chat(models.Model):
    participants = models.ManyToManyField(UserModel,
                                          through='ChatParticipantConnector',
                                          related_name='chats',
                                          symmetrical=True)
    name = models.CharField(unique=False, max_length=50,
                                        blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,
                                unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    last_message_date = models.DateTimeField(default=timezone.now)
    is_group_chat = models.BooleanField(default=False)


    def __str__(self):
        if self.name:
            return self.name
        return str(self.uuid)

    def load_next_15_messages(self, last_saw_date=timezone.now()):
        sortedMessages = self.messages.order_by('-time_stamp')\
            .filter(time_stamp__lt=last_saw_date)[:15]
        if len(sortedMessages) > 0:
            return sortedMessages, sortedMessages[len(sortedMessages)-1].\
                time_stamp
        else:
            return [], last_saw_date

    @property
    def load_last_message(self):
        try:
            lastMessage = self.messages.order_by('-time_stamp') \
                             .filter(time_stamp__lt=timezone.now())[0]
        except IndexError:
            lastMessage = None
        return str(lastMessage)

    def check_if_user_is_a_participant(self, user_id):
        try:
            self.participants.get(pk=user_id)
            return True
        except:
            return False



class Message(models.Model):
    author = models.ForeignKey(UserModel,
                               related_name='author_messages',
                               on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, related_name='messages',
                             on_delete=models.CASCADE)
    content = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(Message,self).save(*args, **kwargs)
        self.chat.last_message_date = timezone.now()
        self.chat.save()

    def __str__(self):
        return self.content

    #useless right now
    def last_15_messages_till_now(self):
        return Message.objects.filter(timeStamp__lte=self.time_stamp)\
            .order_by('-time_stamp')[:15]

    def last_15_messages(self):
        return Message.objects.order_by('-time_stamp').all()[:15]


class ChatParticipantConnector(models.Model):
    chat = models.ForeignKey(Chat,
                             related_name='connector_chat',
                             on_delete=models.CASCADE)
    participant = models.ForeignKey(UserModel,
                                    related_name='connector_par',
                                    on_delete=models.CASCADE)
