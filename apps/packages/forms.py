from django import forms

from apps.core.forms import SlugUniqueMixin
from apps.media.widgets import MediaPickerWidget

from .models import Package, SubPackage


class PackageForm(SlugUniqueMixin, forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Package
        fields = [
            "title",
            "slug",
            "description",
            "image",
            "package_type",
            "is_active",
            "meta_title",
            "meta_description",
            "meta_keywords",
        ]
        labels = {"is_active": "Active"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "image": MediaPickerWidget(),
        }


class SubPackageForm(SlugUniqueMixin, forms.ModelForm):
    slug = forms.SlugField(required=False)

    # Replaces the old `amenities` Textarea — accepts comma-separated input
    # and is converted to/from the JSONField list in __init__ / clean / save.
    amenities_input = forms.CharField(
        required=False,
        label="Amenities",
        widget=forms.TextInput(attrs={"placeholder": "WiFi, Pool, Breakfast"}),
        help_text="Comma-separated list of amenities.",
    )

    class Meta:
        model = SubPackage
        # `amenities` is intentionally absent — handled via amenities_input
        fields = [
            "title",
            "slug",
            "description",
            "image",
            "price",
            "capacity",
            "beds",
            "is_active",
            "meta_title",
            "meta_description",
            "meta_keywords",
        ]
        labels = {"is_active": "Active"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "image": MediaPickerWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the text input from the stored JSON list so that
        # editing an existing SubPackage round-trips cleanly.
        if self.instance and self.instance.pk and self.instance.amenities:
            self.fields["amenities_input"].initial = ", ".join(self.instance.amenities)

    def clean_amenities_input(self):
        raw = self.cleaned_data.get("amenities_input", "")
        if not raw.strip():
            return []
        return [item.strip() for item in raw.split(",") if item.strip()]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.amenities = self.cleaned_data["amenities_input"]
        if commit:
            instance.save()
        return instance
