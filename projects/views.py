from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from projects.models import Project
from projects.serializer import ProjectSerializer, ProjectListSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        project.contributors.add(self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer
