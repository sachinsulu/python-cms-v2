from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Article


class ArticleForm(forms.ModelForm):
    remove_image = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    slug = forms.SlugField(
        required=False,
        help_text='Auto-generated from title. Edit if needed.',
    )

    class Meta:
        model  = Article
        fields = [
            'title', 'subtitle', 'slug', 'content', 'image',
            'meta_title', 'meta_description', 'meta_keywords',
        ]
        widgets = {
            'title':    forms.TextInput(attrs={'placeholder': 'Article title'}),
            'subtitle': forms.TextInput(attrs={'placeholder': 'Optional subtitle'}),
            'content':  forms.Textarea(attrs={'rows': 16}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image or not hasattr(image, 'size'):
            return image
        # Skip validation if unchanged
        if self.instance.pk and image == self.instance.image:
            return image
        max_size = getattr(settings, 'IMAGE_MAX_FILE_SIZE', 2 * 1024 * 1024)
        allowed  = getattr(settings, 'IMAGE_ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'webp'])
        if image.size > max_size:
            raise ValidationError(f'Image too large. Max {max_size // (1024*1024)}MB.')
        ext = image.name.rsplit('.', 1)[-1].lower()
        if ext not in allowed:
            raise ValidationError(f'Invalid type ".{ext}". Allowed: {", ".join(allowed)}')
        return image

    def save(self, commit=True):
        article = super().save(commit=False)
        # Handle image removal from JS signal
        if self.cleaned_data.get('remove_image') == '1':
            if article.image:
                article.image.delete(save=False)
            article.image = None
        if commit:
            article.save()
        return article
