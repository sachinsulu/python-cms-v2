from django import forms
from apps.media.widgets import MediaPickerWidget
from .models import Blog


class BlogForm(forms.ModelForm):
    slug = forms.SlugField(required=False, help_text='Auto-generated from title.')

    class Meta:
        model  = Blog
        fields = ['title', 'subtitle', 'slug', 'date', 'content', 'image', 'banner_image',
                  'meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'title':        forms.TextInput(attrs={'placeholder': 'Blog title'}),
            'content':      forms.Textarea(attrs={'rows': 16}),
            'date':         forms.DateInput(attrs={'type': 'date'}),
            'image':        MediaPickerWidget(),
            'banner_image': MediaPickerWidget(),
        }
