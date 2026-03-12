"""
Generic CMS Views
=================
Base classes for list, create, and update views.
Each content app subclasses these and sets a handful of class attributes.

Adding a new content type = 3 tiny view classes + URLs. Nothing else to change.

list_columns API
----------------
Each entry is a 2-tuple: (field_path, header_label)

field_path supports:
  - plain field names: 'title', 'slug', 'is_active'
  - dot-traversal:     'author.username'
  - method names:      'get_package_type_display'

Built-in magic column keys (handled by the template without get_attr):
  - 'title'     → rendered as an edit link + optional subtitle/name sub-line
  - 'is_active' → rendered as a toggle switch
  - '__actions__' → edit + delete buttons (always appended automatically)

Custom rendering beyond the built-ins is handled via the
`column_renderers` dict (see SubPackageListView for an example).
"""
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from .mixins import CMSPermissionMixin
from .audit import log_action
from .cache import invalidate_dashboard_cache
from .models import AuditLog


class ContentListView(CMSPermissionMixin, View):
    """
    Generic list view for a content model.

    Attributes:
        model               Django model class
        template            Template path (defaults to generic/list.html)
        permission_required e.g. 'articles.view_article'
        extra_context       Extra dict merged into template context
        page_title          Shown in the page header
        create_url          URL name for the Add button
        model_key           Registry key — used by JS for toggle/delete/sort
        edit_url_name       URL name for the per-row edit link
        list_columns        List of (field_path, header_label) tuples
    """
    model         = None
    template      = 'generic/list.html'
    extra_context = None
    page_title    = ''
    create_url    = None
    model_key     = None
    edit_url_name = None

    list_columns = [
        ('title',     'Title'),
        ('slug',      'Slug'),
        ('is_active', 'Status'),
    ]

    def get_extra_context(self):
        return self.extra_context or {}

    def get_queryset(self):
        return self.model.objects.all()

    def get(self, request):
        return render(request, self.template, {
            'list':          self.get_queryset(),
            'model_key':     self.model_key or self.model.__name__.lower(),
            'page_title':    self.page_title or f'{self.model.__name__}s',
            'create_url':    self.create_url,
            'list_columns':  self.list_columns,
            'edit_url_name': self.edit_url_name,
            **self.get_extra_context(),
        })


class ContentCreateView(CMSPermissionMixin, View):
    """
    Generic create view for a content model.

    Hooks:
        before_save(request, obj)  — set author, flags, parent FK, etc.
        get_success_redirect(obj)  — override for custom post-save redirect.
    """
    model         = None
    form_class    = None
    template      = 'generic/form.html'
    list_url      = None
    edit_url      = None
    page_title    = ''
    model_key     = None
    extra_context = None

    def get_extra_context(self):
        return self.extra_context or {}

    def _build_context(self, form):
        """
        Single source of truth for the create-view template context.
        Replaces the 3 copy-pasted inline dicts from the original.
        """
        return {
            'form':       form,
            'page_title': self.page_title or f'Add {self.model.__name__}',
            'list_url':   self.list_url,
            'is_edit':    False,
            'model_key':  self.model_key or (self.model.__name__.lower() if self.model else ''),
            **self.get_extra_context(),
        }

    def get_form(self, data=None, files=None):
        return self.form_class(data, files)

    def before_save(self, request, obj):
        pass

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect(self.list_url)
        if action == 'save_and_new':
            return redirect(self.request.path)
        if self.edit_url:
            identifier = getattr(obj, 'slug', getattr(obj, 'pk', None))
            return redirect(reverse(self.edit_url, args=[identifier]))
        return redirect(self.list_url)

    def get(self, request):
        return render(request, self.template, self._build_context(self.get_form()))

    def post(self, request):
        form = self.get_form(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            self.before_save(request, obj)
            obj.save()
            invalidate_dashboard_cache()
            log_action(request, AuditLog.CREATE, obj)
            messages.success(request, f'"{obj}" created successfully.')
            return self.get_success_redirect(obj)

        return render(request, self.template, self._build_context(form))


class ContentUpdateView(CMSPermissionMixin, View):
    """
    Generic update view for a content model.
    Looked up by slug by default — override get_object() for pk lookups.
    """
    model         = None
    form_class    = None
    template      = 'generic/form.html'
    list_url      = None
    edit_url      = None
    page_title    = ''
    model_key     = None
    extra_context = None

    def get_extra_context(self):
        return self.extra_context or {}

    def _build_context(self, form, obj):
        """
        Single source of truth for the update-view template context.
        Replaces the 2 copy-pasted inline dicts from the original.
        """
        return {
            'form':       form,
            'object':     obj,
            'page_title': self.page_title or f'Edit {self.model.__name__}',
            'list_url':   self.list_url,
            'is_edit':    True,
            'model_key':  self.model_key or (self.model.__name__.lower() if self.model else ''),
            **self.get_extra_context(),
        }

    def get_object(self, **kwargs):
        slug = kwargs.get('slug')
        pk   = kwargs.get('pk')
        if slug:
            return get_object_or_404(self.model, slug=slug)
        return get_object_or_404(self.model, pk=pk)

    def get_form(self, instance, data=None, files=None):
        return self.form_class(data, files, instance=instance)

    def before_save(self, request, obj):
        pass

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect(self.list_url)
        if self.edit_url:
            identifier = getattr(obj, 'slug', getattr(obj, 'pk', None))
            return redirect(reverse(self.edit_url, args=[identifier]))
        return redirect(self.list_url)

    def get(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        return render(request, self.template, self._build_context(self.get_form(obj), obj))

    def post(self, request, *args, **kwargs):
        obj  = self.get_object(**kwargs)
        form = self.get_form(obj, request.POST, request.FILES)

        if form.is_valid():
            old_values = {
                field: str(getattr(obj, field))
                for field in form.changed_data
                if hasattr(obj, field)
            }
            updated = form.save(commit=False)
            self.before_save(request, updated)
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

        return render(request, self.template, self._build_context(form, obj))