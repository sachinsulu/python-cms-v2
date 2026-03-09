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
        ('title',                   'Title'),
        ('get_package_type_display','Type'),
        ('is_active',               'Status'),
        ('sub_packages',            'Sub-Packages'),   # special column rendered by generic/list.html
    ]

    def get_queryset(self):
        from django.db.models import Count
        return Package.objects.select_related('image').annotate(
            sub_package_count=Count('sub_packages')
        ).all()


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
# Sub-packages — parent-scoped list, fully in the generic machinery
# ---------------------------------------------------------------------------

class SubPackageListView(ContentListView):
    """
    List view for SubPackages scoped to a parent Package.

    Uses packages/subpackage_list.html, which extends generic/list.html and
    only overrides header_extras + table_row (for parent-scoped edit URLs).
    All DataTables, sorting, and bulk action machinery is inherited.
    """
    model               = SubPackage
    template            = 'packages/subpackage_list.html'
    permission_required = 'packages.view_subpackage'
    model_key           = 'subpackage'
    edit_url_name       = None    # not used — subpackage_list.html handles its own edit URL

    list_columns = [
        ('title',    'Title'),
        ('slug',     'Slug'),
        ('price',    'Price'),
        ('capacity', 'Capacity'),
        ('is_active','Status'),
    ]

    def _get_package(self):
        return get_object_or_404(Package, slug=self.kwargs.get('package_slug'))

    def get_queryset(self):
        return SubPackage.objects.filter(package=self._get_package()).select_related('image')

    def get_extra_context(self):
        package = self._get_package()
        return {
            'parent':     package,
            # Passed so the template's header_extras block can use it
            'back_url':   reverse('package_list'),
            # Override create_url to point at the sub-package creator
            'create_url': None,   # suppressed — we render the button in header_extras
            # We pass these so the Actions column can build the correct edit URL.
            # The template uses 'subpackage_edit_url_name_with_parent' sentinel to switch.
            'subpackage_parent_slug': package.slug,
        }

    def get(self, request, package_slug):
        self.kwargs = {'package_slug': package_slug}
        package = self._get_package()

        # page_title is dynamic — set before calling super()
        self.page_title = f'{package.title} — Sub-Packages'

        # Inject a custom create URL into extra_context for the header_extras block
        self.extra_context = {
            **self.get_extra_context(),
            'subpackage_create_url': reverse('subpackage_create', kwargs={'package_slug': package.slug}),
        }
        return super().get(request)


class SubPackageCreateView(ContentCreateView):
    model               = SubPackage
    form_class          = SubPackageForm
    permission_required = 'packages.add_subpackage'
    page_title          = 'Add Sub-Package'
    model_key           = 'subpackage'

    def _get_package(self):
        return get_object_or_404(Package, slug=self.kwargs.get('package_slug'))

    def before_save(self, request, obj):
        obj.package = self._get_package()

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect('subpackage_list', package_slug=obj.package.slug)
        return redirect('subpackage_edit', package_slug=obj.package.slug, slug=obj.slug)

    def get(self, request, package_slug):
        self.kwargs = {'package_slug': package_slug}
        package = self._get_package()
        self.extra_context = {'back_url': reverse('subpackage_list', kwargs={'package_slug': package.slug})}
        return super().get(request)

    def post(self, request, package_slug):
        self.kwargs = {'package_slug': package_slug}
        package = self._get_package()
        self.extra_context = {'back_url': reverse('subpackage_list', kwargs={'package_slug': package.slug})}
        return super().post(request)


class SubPackageUpdateView(ContentUpdateView):
    model               = SubPackage
    form_class          = SubPackageForm
    permission_required = 'packages.change_subpackage'
    page_title          = 'Edit Sub-Package'
    model_key           = 'subpackage'

    def _get_package(self):
        return get_object_or_404(Package, slug=self.kwargs.get('package_slug'))

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect('subpackage_list', package_slug=obj.package.slug)
        return redirect('subpackage_edit', package_slug=obj.package.slug, slug=obj.slug)

    def get(self, request, package_slug, slug):
        self.kwargs = {'package_slug': package_slug}
        package = self._get_package()
        self.extra_context = {'back_url': reverse('subpackage_list', kwargs={'package_slug': package.slug})}
        return super().get(request, slug)

    def post(self, request, package_slug, slug):
        self.kwargs = {'package_slug': package_slug}
        package = self._get_package()
        self.extra_context = {'back_url': reverse('subpackage_list', kwargs={'package_slug': package.slug})}
        return super().post(request, slug)