from django.contrib.auth.hashers import make_password
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

    def create(self, validated_data):
        # hash password before saving it to db (required to authenticate users properly)
        validated_data["password"] = make_password(
            validated_data.get("password")
        )
        return super(UserSerializer, self).create(validated_data)
