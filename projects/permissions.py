from rest_framework import permissions
from projects.models import Project, Issue
from users.models import User


class ProjectPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == "list" or view.action == "create":
            return request.auth
        if view.action in [
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.auth:
            return False

        if view.action == "retrieve":
            return (
                obj.author == request.user
                or request.user in obj.contributors.all()
                or request.user.is_superuser
            )
        elif view.action in ["update", "partial_update", "destroy"]:
            return obj.author == request.user or request.user.is_superuser
        else:
            return False


class IssuePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == "list":
            return False
        elif view.action == "create":
            project_pk = request.data.__getitem__("project")
            project = Project.objects.get(pk=project_pk)
            if project and (
                project.author == request.user
                or request.user in project.contributors.all()
            ):
                assigned_to = User.objects.get(
                    pk=request.data.get("assigned_to")
                )
                return assigned_to in project.contributors.all()
            return False
        if view.action in [
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.auth:
            return False

        if view.action == "retrieve":
            return (
                obj.author == request.user
                or request.user in obj.project.contributors.all()
                or request.user.is_superuser
            )
        elif view.action in ["update", "partial_update", "destroy"]:
            return obj.author == request.user or request.user.is_superuser
        else:
            return False


class CommentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == "list":
            return False
        elif view.action == "create":
            issue_pk = request.data.__getitem__("issue")
            issue = Issue.objects.get(pk=issue_pk)
            if issue and (
                issue.author == request.user
                or request.user in issue.project.contributors.all()
            ):
                return True
            return False
        if view.action in [
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.auth:
            return False

        if view.action == "retrieve":
            return (
                obj.author == request.user
                or request.user in obj.issue.project.contributors.all()
                or request.user.is_superuser
            )
        elif view.action in ["update", "partial_update", "destroy"]:
            return obj.author == request.user or request.user.is_superuser
        else:
            return False
