from django.db.models import Prefetch
from rest_framework import serializers, viewsets

from apps.media.api import MediaAssetSerializer

from .models import Package, SubPackage


class SubPackageSerializer(serializers.ModelSerializer):
    image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = SubPackage
        fields = [
            'slug', 'title', 'description', 'image',
            'price', 'capacity', 'beds', 'amenities', 'position',
        ]


class PackageSerializer(serializers.ModelSerializer):
    """
    Serializer for Package with nested active-only sub-packages.

    sub_packages uses a SerializerMethodField instead of the default
    related-field serializer so that inactive sub-packages are excluded
    from the API response.  The PackageViewSet prefetches active
    sub-packages into the `active_sub_packages` attribute via a named
    Prefetch object, so the method reads from that pre-fetched list and
    fires no additional queries.  A queryset fallback is included for
    contexts that don't use the Prefetch (e.g. unit tests, shell usage).
    """

    sub_packages         = serializers.SerializerMethodField()
    package_type_display = serializers.CharField(
        source='get_package_type_display', read_only=True
    )
    image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Package
        fields = [
            'slug', 'title', 'description', 'image',
            'package_type', 'package_type_display', 'position',
            'sub_packages',
        ]

    def get_sub_packages(self, obj):
        # Prefer the pre-fetched list populated by PackageViewSet's Prefetch.
        # Fall back to a live query when the serializer is used outside that
        # context (tests, shell, management commands).
        active = getattr(obj, 'active_sub_packages', None)
        if active is None:
            active = (
                obj.sub_packages
                .filter(is_active=True)
                .select_related('image')
                .order_by('position', 'pk')
            )
        return SubPackageSerializer(
            active, many=True, context=self.context
        ).data


# ---------------------------------------------------------------------------
# Prefetch queryset reused by PackageViewSet
# ---------------------------------------------------------------------------

_ACTIVE_SUB_PACKAGES_PREFETCH = Prefetch(
    'sub_packages',
    queryset=(
        SubPackage.objects
        .filter(is_active=True)
        .select_related('image')
        .order_by('position', 'pk')
    ),
    # to_attr stores the result as a plain list on each Package instance.
    # PackageSerializer.get_sub_packages() reads from this list directly,
    # so iterating over nested sub-packages costs zero extra DB queries.
    to_attr='active_sub_packages',
)


class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Package.objects
        .published()
        .select_related('image')
        .prefetch_related(_ACTIVE_SUB_PACKAGES_PREFETCH)
    )
    serializer_class = PackageSerializer
    lookup_field     = 'slug'


class SubPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Flat endpoint for sub-packages.
    Filters by own is_active AND parent package's is_active so that
    sub-packages of a disabled package are never surfaced.
    """

    queryset = (
        SubPackage.objects
        .published()
        .filter(package__is_active=True)
        .select_related('image')
    )
    serializer_class = SubPackageSerializer
    lookup_field     = 'slug'