from django.db.models import Q
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


from api_projects.models import Project, Issue
from api_projects.serializers import ProjectSerializer, IssueSerializer
from api_projects.permissions import IsOwner, MemberReadOnly, IsProjectMember, CanViewIssues

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
    permission_classes = [IsAuthenticated, IsOwner | MemberReadOnly]

    def get_queryset(self):
        user = self.request.user
        query = Q(owner=user) | Q(members=user)
        return Project.objects.filter(query).distinct()

    @action(methods=["get"], detail=True, url_path="issues", url_name="issues",
            permission_classes=[CanViewIssues])
    def get_issues(self, request, pk=None):
        """
        Additional endpoint for related issues. Available from route: `<project_pk>/issues`.
        """

        project = get_object_or_404(Project, pk=pk)
        serializer = IssueSerializer(project.issues.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get_queryset(self):
        user = self.request.user
        query = Q(project__in=user.projects.all()) | Q(project__in=user.own_projects.all())
        return Issue.objects.filter(query)
