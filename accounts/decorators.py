from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=None):
    """
    Decorator to restrict view access to specific roles.
    Superusers automatically bypass restrictions.
    """
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, "You do not have permission to access this page.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator


def super_admin_required(view_func):
    return role_required(['SUPER_ADMIN'])(view_func)

def hr_required(view_func):
    return role_required(['SUPER_ADMIN', 'HR_ADMIN'])(view_func)

def manager_required(view_func):
    return role_required(['SUPER_ADMIN', 'HR_ADMIN', 'DEPT_MANAGER'])(view_func)

def technician_required(view_func):
    return role_required(['SUPER_ADMIN', 'HR_ADMIN', 'TECHNICIAN'])(view_func)
