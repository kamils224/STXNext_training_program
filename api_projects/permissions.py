from rest_framework.permissions import BasePermission, SAFE_METHODS

from api_projects.models import Project, Issue


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


class MemberReadOnly(BasePermission):
    """
    Object-level permission to only allow members of an object to view it.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `members`.
        return request.method in SAFE_METHODS and request.user in obj.members.all()


class IsProjectMember(BasePermission):
    """
    Checks if current user is member or owner of the project.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `project`.
        if isinstance(obj, Issue):
            return obj.project in request.user.projects.all()
        if isinstance(obj, Project):
            return obj in request.user.projects.all()
