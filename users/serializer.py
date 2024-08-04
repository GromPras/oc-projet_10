import datetime
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

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

        # ensure default values on underaged users account
        birth_date = validated_data["birth_date"]
        today = datetime.date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )
        if age < 15:
            validated_data["can_be_contacted"] = False
            validated_data["can_data_be_shared"] = False
        return super(UserSerializer, self).create(validated_data)
