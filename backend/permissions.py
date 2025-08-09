from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to grant access only to Admin users.
    """
    def has_permission(self, request, view):
        print(f"User Type: {request.user.user_type}") 
        return request.user.is_authenticated and request.user.is_admin_user  # No parentheses

class IsNormalUser(permissions.BasePermission):
    """
    Custom permission to grant access only to Normal users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_normal_user  # No parentheses

class IsPaidUser(permissions.BasePermission):
    """
    Custom permission to grant access only to Paid users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_paid_user  # No parentheses

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin users have full access.
    Normal and Paid users have read-only access.
    Unauthenticated users have no access.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        if getattr(user, 'user_type', None) == 'admin':
            return True
        
        if user.user_type in ['normal', 'paid']:
            return request.method in permissions.SAFE_METHODS
        
        return False
