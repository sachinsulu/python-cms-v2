from rest_framework import serializers
from .models import MediaAsset


class MediaAssetSerializer(serializers.ModelSerializer):
    url           = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model  = MediaAsset
        fields = ['id', 'url', 'thumbnail_url', 'alt_text']

    def get_url(self, obj):
        return obj.url

    def get_thumbnail_url(self, obj):
        return obj.thumbnail_url
