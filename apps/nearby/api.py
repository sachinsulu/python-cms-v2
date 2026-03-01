from rest_framework import serializers, viewsets, filters
from .models import Nearby


class NearbySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Nearby
        fields = [
            'title', 'map_link', 'content', 'distance', 'position', 'is_active'
        ]


class NearbyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Nearby.objects.filter(is_active=True).order_by('position')
    serializer_class = NearbySerializer
    lookup_field     = 'title'
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'content']
