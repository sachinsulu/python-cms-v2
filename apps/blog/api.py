from rest_framework import serializers, viewsets, filters
from .models import Blog
from apps.media.api import MediaAssetSerializer


class BlogSerializer(serializers.ModelSerializer):
    image        = MediaAssetSerializer(read_only=True)
    banner_image = MediaAssetSerializer(read_only=True)
    # Expose the author's display name rather than their PK.
    # SerializerMethodField avoids an extra join when author is NULL.
    author_name  = serializers.SerializerMethodField()

    class Meta:
        model  = Blog
        fields = [
            'slug', 'title', 'subtitle', 'content',
            'image', 'banner_image', 'date',
            'author_name', 'position',
            'meta_title', 'meta_description',
        ]

    def get_author_name(self, obj) -> str | None:
        if obj.author_id is None:
            return None
        return obj.author.get_full_name() or obj.author.username


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Blog.objects
        .published()
        .select_related('image', 'banner_image', 'author')
    )
    serializer_class = BlogSerializer
    lookup_field     = 'slug'
    filter_backends  = [filters.SearchFilter]
    search_fields    = ['title', 'content']
