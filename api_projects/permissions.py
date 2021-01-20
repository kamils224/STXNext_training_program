from rest_framework.permissions import BasePermission, SAFE_METHODS

from api_projects.models import Project, Issue, IssueAttachment


class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        user = request.user
        if isinstance(obj, Project):
            return obj.owner == user
        if isinstance(obj, Issue):
            return obj.owner == user or obj.project.owner == user
        if isinstance(obj, IssueAttachment):
            return obj.issue.owner == user or obj.issue.project.owner == user 

class MemberReadOnly(BasePermission):
    """
    Object-level permission to only allow members of an object to view it.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `members`.
        return request.method in SAFE_METHODS and request.user in obj.members.all()


class CanViewIssues(BasePermission):
    """
    Checks if current can view issues inside projects.
    """

    def has_permission(self, request, view):
        # project id
        pk = view.kwargs["pk"]
        projects = request.user.projects.filter(pk=pk).exists()
        own_projects = request.user.own_projects.filter(pk=pk).exists()
        return projects or own_projects


class IsProjectMember(BasePermission):
    """
    Checks if current user is member of the project.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `project`.
        if isinstance(obj, Issue):
            return obj.project in request.user.projects.all()
        if isinstance(obj, Project):
            return obj in request.user.projects.all()
        if isinstance(obj, IssueAttachment):
            return obj.issue.project in request.user.projects.all()
