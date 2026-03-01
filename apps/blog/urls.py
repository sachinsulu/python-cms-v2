from django.urls import path
from .views import BlogListView, BlogCreateView, BlogUpdateView

urlpatterns = [
    path('',                   BlogListView.as_view(),   name='blog_list'),
    path('create/',            BlogCreateView.as_view(), name='blog_create'),
    path('<slug:slug>/edit/',  BlogUpdateView.as_view(), name='blog_edit'),
]
