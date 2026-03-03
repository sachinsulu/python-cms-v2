"""
Generic CMS Views
=================
Base classes for list, create, and update views.
Each content app subclasses these and sets a handful of class attributes.

Adding a new content type = 3 tiny view classes + URLs. Nothing else to change.
"""
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from .mixins import CMSPermissionMixin
from .audit import log_action
from .cache import invalidate_dashboard_cache
from django.core.exceptions import ValidationError
from .models import AuditLog


class ContentListView(CMSPermissionMixin, View):
    """
    Generic list view for a content model.

    Attributes:
        model           Django model class
        template        Template path (defaults to generic/list.html)
        permission_required  e.g. 'articles.view_article'
        extra_context   Extra dict merged into template context
        page_title      Shown in the page header
        create_url      URL name for the "+ Add" button
        model_key       Registry key — used by JS for toggle/delete/sort
    """
    model           = None
    template        = 'generic/list.html'
    extra_context   = None
    page_title      = ''
    create_url      = None
    model_key       = None

    def get_extra_context(self):
        return self.extra_context or {}

    def get_queryset(self):
        return self.model.objects.all()

    def get(self, request):
        return render(request, self.template, {
            'list':        self.get_queryset(),
            'model_key':   self.model_key or self.model.__name__.lower(),
            'page_title':  self.page_title or f'{self.model.__name__}s',
            'create_url':  self.create_url,
            **self.get_extra_context(),
        })


class ContentCreateView(CMSPermissionMixin, View):
    """
    Generic create view for a content model.

    Hooks:
        before_save(request, obj)  — set author, homepage flag, parent FK, etc.
        get_success_redirect(obj)  — override for custom post-save redirect.
    """
    model           = None
    form_class      = None
    template        = 'generic/form.html'
    list_url        = None
    edit_url        = None    # URL name, e.g. 'article_edit'
    page_title      = ''
    model_key       = None
    extra_context   = None

    def get_extra_context(self):
        return self.extra_context or {}

    def get_form(self, data=None, files=None):
        return self.form_class(data, files)

    def before_save(self, request, obj):
        """Override to inject extra fields before saving."""
        pass

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect(self.list_url)
        if action == 'save_and_new':
            return redirect(self.request.path)
        # Default: stay on edit page
        if self.edit_url:
            return redirect(reverse(self.edit_url, args=[obj.slug]))
        return redirect(self.list_url)

    def get(self, request):
        return render(request, self.template, {
            'form':       self.get_form(),
            'page_title': self.page_title or f'Add {self.model.__name__}',
            'list_url':   self.list_url,
            'is_edit':    False,
            'model_key':  self.model_key or self.model.__name__.lower() if getattr(self, 'model', None) else '',
            **self.get_extra_context(),
        })

    def post(self, request):
        form = self.get_form(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            self.before_save(request, obj)
            try:
                obj.full_clean()
            except ValidationError as e:
                form.add_error(None, e)
                return render(request, self.template, {
                    'form':       form,
                    'page_title': self.page_title or f'Add {self.model.__name__}',
                    'list_url':   self.list_url,
                    'is_edit':    False,
                    'model_key':  self.model_key or self.model.__name__.lower() if getattr(self, 'model', None) else '',
                    **self.get_extra_context(),
                })

            obj.save()
            invalidate_dashboard_cache()
            log_action(request, AuditLog.CREATE, obj)
            messages.success(request, f'"{obj}" created successfully.')
            return self.get_success_redirect(obj)

        return render(request, self.template, {
            'form':       form,
            'page_title': self.page_title or f'Add {self.model.__name__}',
            'list_url':   self.list_url,
            'is_edit':    False,
            'model_key':  self.model_key or self.model.__name__.lower() if getattr(self, 'model', None) else '',
            **self.get_extra_context(),
        })


class ContentUpdateView(CMSPermissionMixin, View):
    """
    Generic update view for a content model.
    Looked up by slug by default — override get_object() for different lookups.
    """
    model           = None
    form_class      = None
    template        = 'generic/form.html'
    list_url        = None
    edit_url        = None
    page_title      = ''
    model_key       = None
    extra_context   = None

    def get_extra_context(self):
        return self.extra_context or {}

    def get_object(self, slug):
        return get_object_or_404(self.model, slug=slug)

    def get_form(self, instance, data=None, files=None):
        return self.form_class(data, files, instance=instance)

    def before_save(self, request, obj):
        pass

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect(self.list_url)
        if self.edit_url:
            return redirect(reverse(self.edit_url, args=[obj.slug]))
        return redirect(self.list_url)

    def get(self, request, slug):
        obj  = self.get_object(slug)
        form = self.get_form(obj)
        return render(request, self.template, {
            'form':       form,
            'object':     obj,
            'page_title': self.page_title or f'Edit {self.model.__name__}',
            'list_url':   self.list_url,
            'is_edit':    True,
            'model_key':  self.model_key or self.model.__name__.lower() if getattr(self, 'model', None) else '',
            **self.get_extra_context(),
        })

    def post(self, request, slug):
        obj  = self.get_object(slug)
        form = self.get_form(obj, request.POST, request.FILES)

        if form.is_valid():
            # Capture what changed for audit log
            old_values = {
                field: str(getattr(obj, field))
                for field in form.changed_data
                if hasattr(obj, field)
            }
            updated = form.save(commit=False)
            self.before_save(request, updated)

            try:
                updated.full_clean()
            except ValidationError as e:
                form.add_error(None, e)
                return render(request, self.template, {
                    'form':       form,
                    'object':     obj,
                    'page_title': self.page_title or f'Edit {self.model.__name__}',
                    'list_url':   self.list_url,
                    'is_edit':    True,
                    'model_key':  self.model_key or self.model.__name__.lower() if getattr(self, 'model', None) else '',
                    **self.get_extra_context(),
                })

            updated.save()
            invalidate_dashboard_cache()
            new_values = {
                field: str(getattr(updated, field))
                for field in form.changed_data
                if hasattr(updated, field)
            }
            log_action(request, AuditLog.UPDATE, updated, changes={
                'before': old_values,
                'after':  new_values,
            })
            messages.success(request, f'"{updated}" saved.')
            return self.get_success_redirect(updated)

        return render(request, self.template, {
            'form':       form,
            'object':     obj,
            'page_title': self.page_title or f'Edit {self.model.__name__}',
            'list_url':   self.list_url,
            'is_edit':    True,
            'model_key':  self.model_key or self.model.__name__.lower() if getattr(self, 'model', None) else '',
            **self.get_extra_context(),
        })
