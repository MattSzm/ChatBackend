import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.urls import reverse


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        if kwargs.get('is_superuser'):
            user.is_staff = True

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **kwargs):
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_superuser', True)
        if kwargs.get('is_superuser') is False:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True,
                              blank=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,
                            unique=True, db_index=True)
    #client side should ask for nickname, just after registration
    username = models.CharField(max_length=50, unique=False,
                                 blank=True, null=True)
    description = models.CharField(max_length=250, blank=True,
                                   null=True)
    photo = models.ImageField(upload_to='users/',
                              blank=True, null=True)
    data_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    friends = models.ManyToManyField('self', through='Contact',
                                        related_name='friends',
                                        symmetrical=True)

    class Meta:
        db_table = 'user'

    USERNAME_FIELD = 'email'
    objects = UserManager()

    @property
    def number_of_chats(self):
        return len(self.chats.all())

    def get_short_name(self):
        return self.username.strip()

    def get_full_name(self):
        return f'{self.uuid}_{self.username}'

    def get_absolute_url(self):
        return reverse('user:fetch-current-user')


class Contact(models.Model):
    first_user = models.ForeignKey(User,
                                   related_name='connector_one_friend',
                                   on_delete=models.CASCADE)
    second_user = models.ForeignKey(User,
                                    related_name='connector_two_friend',
                                    on_delete=models.CASCADE)
    areFriends = models.BooleanField(default=False)
    #when one person send invite to another they are not friends yet
    #we need to switch 'areFriends' to true when second person
    #accept the invitation
    #we display friends by filtring 'areFriends==True'
    #When the invitation is rejected, we delete the object(Contact)

    def __str__(self):
        if self.areFriends:
            pattern = '{} and {} are friends.'
            return self.str_help(pattern)
        else:
            pattern = '{} invited {}.'
            return self.str_help(pattern)

    def str_help(self, pattern):
        if self.first_user.username and self.second_user.username:
            return pattern.format(self.first_user.username,
                                  self.second_user.username)
        elif self.first_user.username:
            return pattern.format(self.first_user.username,
                                  self.second_user.email)
        elif self.second_user.username:
            return pattern.format(self.first_user.email,
                                  self.second_user.username)
        else:
            return pattern.format(self.first_user.email,
                                  self.second_user.email)

