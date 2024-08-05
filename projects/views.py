from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from projects.models import Project, Issue, Comment
from users.models import User
from projects.serializer import (
    ProjectSerializer,
    ProjectListSerializer,
    CommentSerializer,
    ContributorSerializer,
    IssueSerializer,
)
from projects.permissions import (
    ProjectPermission,
    IssuePermission,
    CommentPermission,
)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        contributors = self.request.data.get("contributors", [])
        [
            project.contributors.add(c)
            for c in contributors
            if User.objects.get(pk=c)
        ]
        project.contributors.add(self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def add_contributors(self, request, pk=None):
        project = self.get_object()
        if project.author == request.user or request.user.is_superuser:
            serializer = ContributorSerializer(data=request.data)
            if serializer.is_valid():
                project.contributors.add(
                    *serializer.validated_data["contributor_ids"]  # type: ignore
                )
                project.save()
                return Response(
                    ProjectSerializer(
                        instance=project, context={"request": request}
                    ).data,
                    status.HTTP_200_OK,
                )
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            "Vous n'avez pas la permission de faire ceci",
            status=status.HTTP_403_FORBIDDEN,
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def remove_contributors(self, request, pk=None):
        project = self.get_object()
        if project.author == request.user or request.user.is_superuser:
            serializer = ContributorSerializer(data=request.data)
            if serializer.is_valid():
                project.contributors.remove(
                    *serializer.validated_data["contributor_ids"]  # type: ignore
                )
                project.save()
                return Response(
                    ProjectSerializer(
                        instance=project, context={"request": request}
                    ).data,
                    status.HTTP_200_OK,
                )
            else:
                return Response(
                    serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            "Vous n'avez pas la permission de faire ceci",
            status=status.HTTP_403_FORBIDDEN,
        )

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=LimitOffsetPagination,
    )
    def issues(self, request, pk=None):
        project = self.get_object()
        queryset = project.issue_set.all()
        if (
            request.user == project.author
            or request.user in project.contributors.all()
        ):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            "Vous n'avez pas la permission de faire ceci",
            status=status.HTTP_403_FORBIDDEN,
        )


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IssuePermission]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    @action(
        detail=True,
        methods=["GET"],
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=LimitOffsetPagination,
    )
    def comments(self, request, pk=None):
        issue = self.get_object()
        queryset = issue.comments.all()
        if (
            request.user == issue.author
            or request.user in issue.project.contributors.all()
        ):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = CommentSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response(
            "Vous n'avez pas la permission de faire ceci",
            status=status.HTTP_403_FORBIDDEN,
        )


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [CommentPermission]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)
