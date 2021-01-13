from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api_projects.models import Project
from api_projects.serializers import ProjectSerializer
from api_projects.permissions import IsOwnerOrReadOnly

"""
"Endpoints for:

- creating & editing a new project
- listing all projects available to current user
- assigning user to a project
Project should consist of name, owner and creation date"
"""

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(members__contains=request.user)