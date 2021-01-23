from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import DestroyAPIView, CreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


from api_projects.models import Project, Issue, IssueAttachment
from api_projects.serializers import (
    ProjectSerializer,
    IssueSerializer,
    IssueAttachmentSerializer,
)
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

    def perform_update(self, serializer):
        if (members := self.request.data.get("members", None)) is not None:
            serializer.save(members=members)
        serializer.save()


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


class IssueAttachmentDelete(DestroyAPIView):
    queryset = IssueAttachment.objects.all()
    serializer_class = IssueAttachmentSerializer
    permission_classes = [IsProjectMember | IsOwner]


class IssueAttachmentCreate(CreateAPIView):
    queryset = IssueAttachment.objects.all()
    serializer_class = IssueAttachmentSerializer
    permission_classes = [IsProjectMember | IsOwner]
    parser_classes = [MultiPartParser]
