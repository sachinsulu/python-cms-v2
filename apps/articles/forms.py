from django import forms
from apps.core.forms import SlugUniqueMixin
from apps.media.widgets import MediaPickerWidget
from .models import Article


class ArticleForm(SlugUniqueMixin, forms.ModelForm):
    slug = forms.SlugField(
        required=False,
        help_text='Auto-generated from title. Edit if needed.',
    )

    class Meta:
        model  = Article
        fields = [
            'title', 'subtitle', 'slug', 'content', 'image', 'is_active',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        labels  = {'is_active': 'Active'}
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'Article title'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'Optional subtitle'}),
            'content':  forms.Textarea(attrs={'rows': 16}),
            'image':    MediaPickerWidget(),
        }
