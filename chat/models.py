from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone

UserModel = get_user_model()


class Chat(models.Model):
    participants = models.ManyToManyField(UserModel,
                                          related_name='chats')
    name = models.CharField(unique=False, max_length=50,
                                            blank=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,
                                unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name.split('_',1)[1]

    def load_next_10_messages(self, last_saw_date=timezone.now()):
        sortedMessages = self.messages.order_by('-time_stamp')\
            .filter(time_stamp__lte=last_saw_date)[:10]
        return sortedMessages, sortedMessages[len(sortedMessages)-1].time_stamp



class Message(models.Model):
    author = models.ForeignKey(UserModel,
                               related_name='author_messages',
                               on_delete=models.CASCADE)
    content = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, related_name='messages',
                             on_delete=models.CASCADE)

    def __str__(self):
        return self.author.username

    def last_15_messages_till_now(self):
        return Message.objects.filter(timeStamp__lte=self.time_stamp)\
            .order_by('-time_stamp')[:15 ]

    def last_15_messages(self):
        return Message.objects.order_by('-time_stamp').all()[:15]


