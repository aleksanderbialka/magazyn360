from rest_framework.permissions import BasePermission


class IsInUserCompany(BasePermission):
    """
    Allows access only to users who belong to the same company as the object.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "company")
            and getattr(obj, "company", None) == request.user.company
        )
