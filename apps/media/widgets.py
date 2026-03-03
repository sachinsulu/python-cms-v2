from django import forms
from .models import MediaAsset


class MediaPickerWidget(forms.Widget):
    """
    Custom widget for selecting a MediaAsset via a gallery modal.
    Renders a hidden input (stores asset PK) + preview area + action buttons.
    """
    template_name = 'media/widgets/media_picker.html'

    class Media:
        css = {'all': ['css/media-picker.css']}
        js  = ['js/media-picker.js']

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        # Resolve the current MediaAsset for preview
        asset = None
        if value:
            try:
                asset = MediaAsset.objects.get(pk=value)
            except MediaAsset.DoesNotExist:
                pass

        context['asset'] = asset
        return context

    def value_from_datadict(self, data, files, name):
        val = data.get(name)
        if val == '' or val is None:
            return None
        return val
