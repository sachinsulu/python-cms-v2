from functools import cached_property

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Package, SubPackage
from .forms import PackageForm, SubPackageForm


class PackageListView(ContentListView):
    model               = Package
    permission_required = 'packages.view_package'
    page_title          = 'Packages'
    create_url          = 'package_create'
    model_key           = 'package'
    edit_url_name       = 'package_edit'

    list_columns = [
        ('title',                    'Title'),
        ('get_package_type_display', 'Type'),
        ('is_active',                'Status'),
        ('sub_packages',             'Sub-Packages'),
    ]

    def get_queryset(self):
        from django.db.models import Count
        return (
            Package.objects
            .select_related('image')
            .annotate(sub_package_count=Count('sub_packages'))
            .all()
        )


class PackageCreateView(ContentCreateView):
    model               = Package
    form_class          = PackageForm
    permission_required = 'packages.add_package'
    page_title          = 'Add Package'
    list_url            = 'package_list'
    edit_url            = 'package_edit'
    model_key           = 'package'


class PackageUpdateView(ContentUpdateView):
    model               = Package
    form_class          = PackageForm
    permission_required = 'packages.change_package'
    page_title          = 'Edit Package'
    list_url            = 'package_list'
    edit_url            = 'package_edit'
    model_key           = 'package'


# ---------------------------------------------------------------------------
# Shared mixin — one DB hit per request for the parent Package
# ---------------------------------------------------------------------------

class _PackageScopedMixin:
    """
    Shared by all three SubPackage views.

    Exposes self._package as a cached_property so the parent Package is
    fetched exactly once per request regardless of how many times
    get_extra_context(), before_save(), or get_success_redirect() access it.

    Call self._set_kwargs(package_slug) at the top of every get()/post()
    before any code that touches self._package.
    """

    def _set_kwargs(self, package_slug):
        self.kwargs = {'package_slug': package_slug}

    @cached_property
    def _package(self):
        return get_object_or_404(Package, slug=self.kwargs.get('package_slug'))


class SubPackageListView(_PackageScopedMixin, ContentListView):
    model               = SubPackage
    template            = 'packages/subpackage_list.html'
    permission_required = 'packages.view_subpackage'
    model_key           = 'subpackage'
    edit_url_name       = None

    list_columns = [
        ('title',    'Title'),
        ('slug',     'Slug'),
        ('price',    'Price'),
        ('capacity', 'Capacity'),
        ('is_active','Status'),
    ]

    def get_queryset(self):
        return (
            SubPackage.objects
            .filter(package=self._package)
            .select_related('image')
        )

    def get_extra_context(self):
        # self._package already cached — no second DB hit
        return {
            'parent':                 self._package,
            'back_url':               reverse('package_list'),
            'create_url':             None,
            'subpackage_parent_slug': self._package.slug,
        }

    def get(self, request, package_slug):
        self._set_kwargs(package_slug)
        self.page_title = f'{self._package.title} — Sub-Packages'
        self.extra_context = {
            **self.get_extra_context(),
            'subpackage_create_url': reverse(
                'subpackage_create',
                kwargs={'package_slug': self._package.slug},
            ),
        }
        return super().get(request)


class SubPackageCreateView(_PackageScopedMixin, ContentCreateView):
    model               = SubPackage
    form_class          = SubPackageForm
    permission_required = 'packages.add_subpackage'
    page_title          = 'Add Sub-Package'
    model_key           = 'subpackage'

    def before_save(self, request, obj):
        obj.package = self._package

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect('subpackage_list', package_slug=obj.package.slug)
        return redirect('subpackage_edit', package_slug=obj.package.slug, slug=obj.slug)

    def get(self, request, package_slug):
        self._set_kwargs(package_slug)
        self.extra_context = {
            'back_url': reverse(
                'subpackage_list', kwargs={'package_slug': self._package.slug}
            ),
        }
        return super().get(request)

    def post(self, request, package_slug):
        self._set_kwargs(package_slug)
        self.extra_context = {
            'back_url': reverse(
                'subpackage_list', kwargs={'package_slug': self._package.slug}
            ),
        }
        return super().post(request)


class SubPackageUpdateView(_PackageScopedMixin, ContentUpdateView):
    model               = SubPackage
    form_class          = SubPackageForm
    permission_required = 'packages.change_subpackage'
    page_title          = 'Edit Sub-Package'
    model_key           = 'subpackage'

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect('subpackage_list', package_slug=obj.package.slug)
        return redirect('subpackage_edit', package_slug=obj.package.slug, slug=obj.slug)

    def get(self, request, package_slug, slug):
        self._set_kwargs(package_slug)
        self.extra_context = {
            'back_url': reverse(
                'subpackage_list', kwargs={'package_slug': self._package.slug}
            ),
        }
        return super().get(request, slug=slug)

    def post(self, request, package_slug, slug):
        self._set_kwargs(package_slug)
        self.extra_context = {
            'back_url': reverse(
                'subpackage_list', kwargs={'package_slug': self._package.slug}
            ),
        }
        return super().post(request, slug=slug)