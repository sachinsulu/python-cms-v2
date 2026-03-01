from rest_framework import serializers, viewsets, filters
from .models import Blog


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Blog
        fields = ['slug', 'title', 'subtitle', 'content', 'image',
                  'banner_image', 'date', 'meta_title', 'meta_description', 'created_at']


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Blog.objects.filter(is_active=True).order_by('position')
    serializer_class = BlogSerializer
    lookup_field     = 'slug'
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'content']
