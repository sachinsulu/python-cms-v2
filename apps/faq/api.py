from rest_framework import serializers, viewsets, filters
from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FAQ
        fields = [
            'id', 'title', 'content', 'position', 'is_active'
        ]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = FAQ.objects.filter(is_active=True).order_by('position')
    serializer_class = FAQSerializer
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'content']
