from rest_framework import serializers, viewsets, filters
from .models import Article
from apps.media.api import MediaAssetSerializer



class ArticleSerializer(serializers.ModelSerializer):
    image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Article
        fields = [
            'slug', 'title', 'subtitle', 'content', 'image',
            'homepage', 'meta_title', 'meta_description', 'created_at', 'updated_at',
        ]


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Article.objects.filter(is_active=True).select_related('image').order_by('position')
    serializer_class = ArticleSerializer
    lookup_field     = 'slug'
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'subtitle', 'content']
