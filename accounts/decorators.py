"""Security decorators to protect views"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def committee_director_required(view_func):
    """
    Decorator to ensure user is director of the committee they're accessing.
    Usage: @committee_director_required
    """

    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        from .models import Committee

        try:
            committee = Committee.objects.get(pk=pk)
        except Committee.DoesNotExist:
            messages.error(request, "Committee not found.")
            return redirect("profile")

        # Check if user is director or EXCO
        is_director = committee.director == request.user
        is_exco = request.user.is_exco_or_trustee()

        if not (is_director or is_exco):
            messages.error(
                request, "Access denied. You are not the director of this committee."
            )
            return redirect("profile")

        return view_func(request, pk, *args, **kwargs)

    return wrapper


def committee_member_required(view_func):
    """
    Decorator to ensure user is a member of the committee.
    Usage: @committee_member_required
    """

    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        from .models import Committee

        try:
            committee = Committee.objects.get(pk=pk)
        except Committee.DoesNotExist:
            messages.error(request, "Committee not found.")
            return redirect("profile")

        # Check if user is member, director, or EXCO
        is_member = committee.members.filter(id=request.user.id).exists()
        is_director = committee.director == request.user
        is_exco = request.user.is_exco_or_trustee()

        if not (is_member or is_director or is_exco):
            messages.error(
                request, "Access denied. You are not a member of this committee."
            )
            return redirect("profile")

        return view_func(request, pk, *args, **kwargs)

    return wrapper


def exco_required(view_func):
    """
    Decorator to ensure user is EXCO or Trustee.
    Usage: @exco_required
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_exco_or_trustee():
            raise PermissionDenied("Only EXCO members can access this page.")

        return view_func(request, *args, **kwargs)

    return wrapper


def verified_member_required(view_func):
    """
    Decorator to ensure user is verified.
    Usage: @verified_member_required
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_verified:
            messages.warning(
                request, "This feature is only available to verified members."
            )
            return redirect("profile")

        return view_func(request, *args, **kwargs)

    return wrapper
