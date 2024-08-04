from rest_framework import mixins, viewsets
from users.models import User
from users.serializer import UserSerializer
from users.permissions import UserPermission


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
):
    """
    Provides users related actions
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]
