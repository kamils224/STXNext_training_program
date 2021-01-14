from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrMemberReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it and members to view it.
    Assumes the model instance has an `owner` and `members` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        if obj.owner == request.user:
            return True
        if request.method in SAFE_METHODS:
            # Instance must have an attribute named `members`.
            return request.user in obj.members.all()
        return False
