from rest_framework import serializers, viewsets
from .models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    via_type_display = serializers.CharField(source='get_via_type_display', read_only=True)

    class Meta:
        model  = Testimonial
        fields = ['id', 'title', 'name', 'content', 'rating', 'image',
                  'country', 'linksrc', 'via_type', 'via_type_display', 'position']


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Testimonial.objects.filter(is_active=True).order_by('position')
    serializer_class = TestimonialSerializer
