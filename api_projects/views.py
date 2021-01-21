from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


from api_projects.models import Project, Issue
from api_projects.serializers import ProjectSerializer, IssueSerializer
from api_projects.permissions import (
    IsOwner,
    MemberReadOnly,
    IsProjectMember,
)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwner | MemberReadOnly]

    def get_queryset(self):
        user = self.request.user
        query = Q(owner=user) | Q(members=user)
        return Project.objects.filter(query).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsProjectMember]

    def get_queryset(self):
        user = self.request.user
        query = Q(project__in=user.projects.all()) | Q(
            project__in=user.own_projects.all()
        )
        return Issue.objects.filter(query)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
