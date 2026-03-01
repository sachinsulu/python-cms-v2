from django.urls import path
from . import views

urlpatterns = [
    path('',               views.UserListView.as_view(),   name='user_list'),
    path('create/',        views.UserCreateView.as_view(), name='user_create'),
    path('<int:pk>/edit/', views.UserEditView.as_view(),   name='user_edit'),
    path('<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    path('groups/',               views.GroupListView.as_view(),  name='group_list'),
    path('groups/create/',        views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/edit/', views.GroupEditView.as_view(),   name='group_edit'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),
]
