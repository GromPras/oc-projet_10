import uuid
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


class Issue(models.Model):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PRIORITIES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    ]
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    TAGS = [
        (BUG, "Bug"),
        (FEATURE, "Feature"),
        (TASK, "Task"),
    ]
    TODO = "to-do"
    IN_PROGRESS = "in-progress"
    FINISHED = "finished"
    STATUS = [
        (TODO, "To do"),
        (IN_PROGRESS, "In Progress"),
        (FINISHED, "Finished"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    author = models.ForeignKey(
        User,
        related_name="created_issues",
        on_delete=models.SET(get_sentinel_user), # type: ignore
        default=None,
    )
    assigned_to = models.ForeignKey(User, related_name="assigned_issues", on_delete=models.SET(get_sentinel_user)) # type: ignore
    title = models.CharField(
        max_length=100, blank=False, default=f"Issue {str(time.time).split(".")[0]}"
    )
    description = models.TextField(blank=True)
    priority = models.CharField(
        choices=PRIORITIES, default=MEDIUM, max_length=6
    )
    tag = models.CharField(
        choices=TAGS, default=BUG, max_length=7
    )
    status = models.CharField(
        choices=STATUS, default=TODO, max_length=11
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey("projects.Issue", related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey("users.User", related_name="comments", on_delete=models.SET(get_sentinel_user), default=None) # type: ignore
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
