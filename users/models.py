from django.db import models
from django.contrib.auth.models import AbstractUser


def get_sentinel_user():
    return User.objects.get_or_create(
        username="deleted", birthdate="2024-01-01"
    )[0]


class User(AbstractUser):
    birth_date = models.DateField(blank=False)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ["birth_date"]
