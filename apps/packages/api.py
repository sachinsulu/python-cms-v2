from rest_framework import serializers, viewsets
from .models import Package, SubPackage
from apps.media.api import MediaAssetSerializer



class SubPackageSerializer(serializers.ModelSerializer):
    image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = SubPackage
        fields = ['slug', 'title', 'description', 'image', 'price',
                  'capacity', 'beds', 'amenities', 'position']


class PackageSerializer(serializers.ModelSerializer):
    sub_packages         = SubPackageSerializer(many=True, read_only=True)
    package_type_display = serializers.CharField(source='get_package_type_display', read_only=True)
    image                = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Package
        fields = ['slug', 'title', 'description', 'image',
                  'package_type', 'package_type_display', 'position', 'sub_packages']


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.filter(is_active=True)\
        .select_related('image')\
        .prefetch_related('sub_packages__image')\
        .order_by('position')
    serializer_class = PackageSerializer
    lookup_field     = 'slug'


class SubPackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = SubPackage.objects.filter(is_active=True, package__is_active=True).select_related('image').order_by('position')
    serializer_class = SubPackageSerializer
    lookup_field     = 'slug'
