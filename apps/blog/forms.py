from django import forms
from .models import Blog


class BlogForm(forms.ModelForm):
    remove_image        = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    remove_banner_image = forms.CharField(widget=forms.HiddenInput(), required=False, initial='0')
    slug = forms.SlugField(required=False, help_text='Auto-generated from title.')

    class Meta:
        model  = Blog
        fields = ['title', 'subtitle', 'slug', 'date', 'content', 'image', 'banner_image',
                  'meta_title', 'meta_description', 'meta_keywords']
        widgets = {
            'title':   forms.TextInput(attrs={'placeholder': 'Blog title'}),
            'content': forms.Textarea(attrs={'rows': 16}),
            'date':    forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        blog = super().save(commit=False)
        if self.cleaned_data.get('remove_image') == '1':
            blog.image = None
        if self.cleaned_data.get('remove_banner_image') == '1':
            blog.banner_image = None
        if commit:
            blog.save()
        return blog
