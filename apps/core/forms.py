"""
apps/core/forms.py
==================
Shared form mixins for the CMS.

SlugUniqueMixin
---------------
Validates slug uniqueness at the form layer via a single GlobalSlug query.

Why form layer and not model layer:
  - Model.save() is called during migrations, management commands, bulk
    operations, and tests — contexts where registry/form validation is
    inappropriate.
  - Form validation runs only during user-facing create/update flows.
  - GlobalSlug.slug (PK) provides the remaining DB-level guard for any
    path that bypasses the form.

Usage:
    from apps.core.forms import SlugUniqueMixin

    class ArticleForm(SlugUniqueMixin, forms.ModelForm):
        ...
"""
from django import forms


class SlugUniqueMixin:
    """
    Mixin for any ModelForm with a 'slug' field.
    Performs a single SELECT against GlobalSlug on form validation.
    """

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').strip()

        if not slug:
            # Blank slug is fine — auto-generated from title on save().
            return slug

        from apps.core.registry import cms_registry

        exclude_obj = (
            self.instance
            if (self.instance and self.instance.pk)
            else None
        )

        if cms_registry.is_slug_taken(slug, exclude_obj=exclude_obj):
            raise forms.ValidationError(
                f"The slug '{slug}' is already in use. "
                "Please choose a different slug or adjust the title."
            )

        return slug
