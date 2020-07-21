from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class Message(models.Model):
    author = models.ForeignKey(UserModel,
                               related_name='author_messages',
                               on_delete=models.CASCADE)
    content = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username

    def last_15_messages_till_now(self):
        return Message.objects.filter(timeStamp__lte=self.time_stamp)\
            .order_by('-time_stamp')[:15 ]

    def last_15_messages(self):
        return Message.objects.order_by('-time_stamp').all()[:15]