import user.serializers
from rest_framework.generics import RetrieveAPIView
from user.models import User

class UserDetail(RetrieveAPIView):
    queryset = User.object.all()
    serializer_class = user.serializers.BaseUserSerializer
    lookup_field = 'uuid'
