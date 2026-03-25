from rest_framework import serializers, viewsets, filters
from .models import Nearby


class NearbySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Nearby
        fields = [
            'id', 'title', 'map_link', 'content', 'distance', 'position', 'is_active'
        ]


class NearbyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Nearby.objects.published()
    serializer_class = NearbySerializer
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'content']
