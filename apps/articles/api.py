from rest_framework import serializers, viewsets, filters
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Article
        fields = [
            'slug', 'title', 'subtitle', 'content', 'image',
            'homepage', 'meta_title', 'meta_description', 'created_at', 'updated_at',
        ]


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Article.objects.filter(is_active=True).order_by('position')
    serializer_class = ArticleSerializer
    lookup_field     = 'slug'
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'subtitle', 'content']
