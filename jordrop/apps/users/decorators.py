from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """
    Decorator that checks the logged-in user's role.
    Usage:
        @login_required
        @role_required('moderator', 'admin')
        def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def contributor_required(view_func):
    """Shortcut: requires contributor, moderator, or admin role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_contributor:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def moderator_required(view_func):
    """Shortcut: requires moderator or admin role."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_moderator:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
