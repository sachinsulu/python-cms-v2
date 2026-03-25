from rest_framework import serializers, viewsets, filters
from .models import Article
from apps.media.api import MediaAssetSerializer



class ArticleSerializer(serializers.ModelSerializer):
    image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Article
        fields = [
            'slug', 'title', 'subtitle', 'content', 'image',
            'homepage', 'meta_title', 'meta_description', 'position', 'is_active',
        ]


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Article.objects.published().select_related('image')
    serializer_class = ArticleSerializer
    lookup_field     = 'slug'
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'subtitle', 'content']
