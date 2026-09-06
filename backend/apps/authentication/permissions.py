from rest_framework import permissions

class IsHRAdmin(permissions.BasePermission):
    """Allows access only to HR Admin users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'hr_admin')

class IsManager(permissions.BasePermission):
    """Allows access only to Manager users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'manager')

class IsSystemAdmin(permissions.BasePermission):
    """Allows access only to System Admin users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'system_admin')

class IsEmployee(permissions.BasePermission):
    """Allows access to Employees."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'employee')

class IsOwnerOrHRAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit/view it,
    unless they are an HR Admin.
    Assumes the object has an `employee_id` attribute.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role in ('hr_admin', 'system_admin'):
            return True
        return str(obj.employee_id) == str(request.user.employee_id)
