from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "birth_date",
            "can_be_contacted",
            "can_data_be_shared",
        ]
