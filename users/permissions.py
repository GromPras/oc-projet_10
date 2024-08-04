from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in [
            "list",
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:
            return request.auth
        if view.action == "create":
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # Deny actions on objects if the user is not authenticated
        if not request.auth:
            return False

        if view.action == "retrieve":
            return obj == request.user or request.user.is_superuser
        elif view.action in ["update", "partial_update", "destroy"]:
            return obj == request.user or request.user.is_superuser
        else:
            return False
