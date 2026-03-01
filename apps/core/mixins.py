"""
View Mixins
===========
Reusable mixins for permission checking and shared view behaviour.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages


class CMSPermissionMixin(LoginRequiredMixin):
    """
    Extends LoginRequiredMixin with Django permission checking.

    Set `permission_required` on the view class:
        permission_required = 'articles.view_article'
    or leave unset to just require login.
    """
    permission_required: str | None = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.permission_required:
            if not (request.user.is_superuser or request.user.has_perm(self.permission_required)):
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard')

        return super().dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin(LoginRequiredMixin):
    """Restricts a view to superusers only."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            messages.error(request, "This page is restricted to administrators.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
