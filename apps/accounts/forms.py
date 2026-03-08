from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        required=False,
        help_text='Leave blank to keep existing password (when editing).'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'groups']

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd  = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['groups'])
        return user


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.exclude(
            content_type__app_label__in=['admin', 'contenttypes', 'sessions']
        ).select_related('content_type'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model  = Group
        fields = ['name', 'permissions']
