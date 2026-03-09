from rest_framework import serializers, viewsets, filters
from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FAQ
        fields = [
            'slug', 'title', 'content', 'position', 'is_active'
        ]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = FAQ.objects.all().order_by('position')
    serializer_class = FAQSerializer
    lookup_field     = 'slug'
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'content']
