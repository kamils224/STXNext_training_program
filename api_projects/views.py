from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api_projects.models import Project
from api_projects.serializers import ProjectSerializer
from api_projects.permissions import IsOwnerOrMemberReadOnly


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMemberReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(Q(members=user) | Q(owner=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
