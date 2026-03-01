from django.shortcuts import get_object_or_404, redirect
from apps.core.generic_views import ContentListView, ContentCreateView, ContentUpdateView
from .models import Package, SubPackage
from .forms import PackageForm, SubPackageForm


class PackageListView(ContentListView):
    model               = Package
    permission_required = 'packages.view_package'
    page_title          = 'Packages'
    create_url          = 'package_create'
    model_key           = 'package'


class PackageCreateView(ContentCreateView):
    model               = Package
    form_class          = PackageForm
    permission_required = 'packages.add_package'
    page_title          = 'Add Package'
    list_url            = 'package_list'
    edit_url            = 'package_edit'


class PackageUpdateView(ContentUpdateView):
    model               = Package
    form_class          = PackageForm
    permission_required = 'packages.change_package'
    page_title          = 'Edit Package'
    list_url            = 'package_list'
    edit_url            = 'package_edit'


# Sub-packages — slightly different: needs parent Package
class SubPackageListView(ContentListView):
    model               = SubPackage
    permission_required = 'packages.view_subpackage'
    model_key           = 'subpackage'

    def get_package(self):
        return get_object_or_404(Package, slug=self.kwargs['package_slug'])

    def get_queryset(self):
        return SubPackage.objects.filter(package=self.get_package())

    def get(self, request, package_slug):
        self.kwargs = {'package_slug': package_slug}
        package = self.get_package()
        from django.shortcuts import render
        return render(request, 'generic/list.html', {
            'list':       self.get_queryset(),
            'model_key':  'subpackage',
            'page_title': f'{package.title} — Sub-Packages',
            'create_url': 'subpackage_create',
            'parent':     package,
        })


class SubPackageCreateView(ContentCreateView):
    model               = SubPackage
    form_class          = SubPackageForm
    permission_required = 'packages.add_subpackage'
    page_title          = 'Add Sub-Package'

    def get_package(self):
        return get_object_or_404(Package, slug=self.kwargs['package_slug'])

    def before_save(self, request, obj):
        obj.package = self.get_package()

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect('subpackage_list', package_slug=obj.package.slug)
        return redirect('subpackage_edit', package_slug=obj.package.slug, slug=obj.slug)

    def get(self, request, package_slug):
        self.kwargs = {'package_slug': package_slug}
        return super().get(request)

    def post(self, request, package_slug):
        self.kwargs = {'package_slug': package_slug}
        return super().post(request)


class SubPackageUpdateView(ContentUpdateView):
    model               = SubPackage
    form_class          = SubPackageForm
    permission_required = 'packages.change_subpackage'
    page_title          = 'Edit Sub-Package'

    def get_package(self):
        return get_object_or_404(Package, slug=self.kwargs['package_slug'])

    def get_success_redirect(self, obj):
        action = self.request.POST.get('action', 'save')
        if action == 'save_and_quit':
            return redirect('subpackage_list', package_slug=obj.package.slug)
        return redirect('subpackage_edit', package_slug=obj.package.slug, slug=obj.slug)

    def get(self, request, package_slug, slug):
        self.kwargs = {'package_slug': package_slug}
        return super().get(request, slug)

    def post(self, request, package_slug, slug):
        self.kwargs = {'package_slug': package_slug}
        return super().post(request, slug)
