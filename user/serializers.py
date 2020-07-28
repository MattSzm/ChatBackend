from rest_framework import serializers
from user.models import User

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'uuid', 'user_name', 'photo', 'is_active']