from rest_framework import serializers, viewsets
from .models import Social
from apps.media.api import MediaAssetSerializer




class SocialSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Social
        fields = ['id', 'title', 'link', 'image', 'icon', 'type', 'type_display', 'position']


class SocialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Social.objects.published().select_related('image')
    serializer_class = SocialSerializer

    def get_queryset(self):
        qs          = super().get_queryset()
        type_filter = self.request.query_params.get('type')
        if type_filter in (Social.TYPE_SOCIAL, Social.TYPE_OTA):
            qs = qs.filter(type=type_filter)
        return qs
