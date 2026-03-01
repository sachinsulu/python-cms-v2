from django.urls import path
from .views import (PackageListView, PackageCreateView, PackageUpdateView,
                    SubPackageListView, SubPackageCreateView, SubPackageUpdateView)

urlpatterns = [
    path('',                        PackageListView.as_view(),   name='package_list'),
    path('create/',                 PackageCreateView.as_view(), name='package_create'),
    path('<slug:slug>/edit/',        PackageUpdateView.as_view(), name='package_edit'),
    path('<slug:package_slug>/sub/', SubPackageListView.as_view(),   name='subpackage_list'),
    path('<slug:package_slug>/sub/create/', SubPackageCreateView.as_view(), name='subpackage_create'),
    path('<slug:package_slug>/sub/<slug:slug>/edit/', SubPackageUpdateView.as_view(), name='subpackage_edit'),
]
