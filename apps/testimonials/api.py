from rest_framework import serializers, viewsets
from .models import Testimonial
from apps.media.api import MediaAssetSerializer



class TestimonialSerializer(serializers.ModelSerializer):
    image = MediaAssetSerializer(read_only=True)

    class Meta:
        model  = Testimonial
        fields = ['id', 'title', 'name', 'content', 'rating', 'image',
                  'country', 'linksrc', 'via_type', 'position']


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Testimonial.objects.published().select_related('image')
    serializer_class = TestimonialSerializer
