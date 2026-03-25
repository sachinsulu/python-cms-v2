from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib import messages


from apps.core.mixins import CMSPermissionMixin, SuperuserRequiredMixin
from apps.core.cache import invalidate_dashboard_cache
from .forms import LoginForm, UserCreateForm, GroupForm

User = get_user_model()


# ------------------------------------------------------------------ #
# Auth
# ------------------------------------------------------------------ #

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'dashboard'))
            messages.error(request, 'Invalid username or password.')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('login')


# ------------------------------------------------------------------ #
# User management (superuser only)
# ------------------------------------------------------------------ #

class UserListView(SuperuserRequiredMixin, View):
    def get(self, request):
        users = User.objects.prefetch_related('groups').order_by('username')
        return render(request, 'users/list.html', {'users': users})


class UserCreateView(SuperuserRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/form.html', {'form': UserCreateForm(), 'is_edit': False})

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_list')
        return render(request, 'users/form.html', {'form': form, 'is_edit': False})


class UserEditView(SuperuserRequiredMixin, View):
    def get_user(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        user = self.get_user(pk)
        form = UserCreateForm(instance=user)
        return render(request, 'users/form.html', {'form': form, 'is_edit': True, 'object': user})

    def post(self, request, pk):
        user = self.get_user(pk)
        form = UserCreateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            invalidate_dashboard_cache()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
        return render(request, 'users/form.html', {'form': form, 'is_edit': True, 'object': user})


class UserDeleteView(SuperuserRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_superuser:
            messages.error(request, 'Cannot delete a superuser account.')
        elif user == request.user:
            messages.error(request, 'Cannot delete your own account.')
        else:
            user.delete()
            invalidate_dashboard_cache()
            messages.success(request, f'User "{user.username}" deleted.')
        return redirect('user_list')


# ------------------------------------------------------------------ #
# Group management (superuser only)
# ------------------------------------------------------------------ #

class GroupListView(SuperuserRequiredMixin, View):
    def get(self, request):
        groups = Group.objects.prefetch_related('permissions').order_by('name')
        return render(request, 'users/group_list.html', {'groups': groups})


class GroupCreateView(SuperuserRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/group_form.html', {'form': GroupForm(), 'is_edit': False})

    def post(self, request):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group created.')
            return redirect('group_list')
        return render(request, 'users/group_form.html', {'form': form, 'is_edit': False})


class GroupEditView(SuperuserRequiredMixin, View):
    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        return render(request, 'users/group_form.html', {'form': GroupForm(instance=group), 'is_edit': True, 'object': group})

    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        form  = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            invalidate_dashboard_cache()
            messages.success(request, 'Group updated.')
            return redirect('group_list')
        return render(request, 'users/group_form.html', {'form': form, 'is_edit': True, 'object': group})


class GroupDeleteView(SuperuserRequiredMixin, View):
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        group_name = group.name
        group.delete()
        invalidate_dashboard_cache()
        messages.success(request, f'Group "{group_name}" deleted.')
        return redirect('group_list')
