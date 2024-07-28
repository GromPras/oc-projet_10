from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from projects.models import Project
from projects.serializer import ProjectSerializer


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)
        project.contributors.add(self.request.user)
