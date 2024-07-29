from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from projects.models import Project, Issue
from projects.serializer import (
    ProjectSerializer,
    ProjectListSerializer,
    ContributorSerializer,
    IssueSerializer,
)
from projects.permissions import ProjectPermission, IssuePermission


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, ProjectPermission]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
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
    )
    def issues(self, request, pk=None):
        project = self.get_object()
        if (
            request.user == project.author
            or request.user in project.contributors.all()
        ):
            issues = project.issue_set.all()
            return Response(
                IssueSerializer(issues, many=True).data,
                status.HTTP_200_OK,
            )
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
