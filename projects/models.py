import time
from django.db import models
from users.models import get_sentinel_user, User


class Project(models.Model):
    BACKEND = "back-end"
    FRONTEND = "front-end"
    ANDROID = "android"
    IOS = "ios"
    CATEGORIES = [
        (BACKEND, "Back-End"),
        (FRONTEND, "Front-End"),
        (ANDROID, "Android"),
        (IOS, "iOS"),
    ]
    title = models.CharField(
        max_length=100, blank=False, default=f"Project {str(time.time).split(".")[0]}"
    )
    description = models.TextField(blank=True)
    category = models.CharField(
        choices=CATEGORIES, default=BACKEND, max_length=9
    )
    author = models.ForeignKey(
        "users.User",
        related_name="projects",
        on_delete=models.SET(get_sentinel_user), # type: ignore
        default=None,
    )
    contributors = models.ManyToManyField(User, through="Contributor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contributor(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user)) # type: ignore
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
