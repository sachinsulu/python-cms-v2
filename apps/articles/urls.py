from django.urls import path
from .views import ArticleListView, ArticleCreateView, ArticleUpdateView

urlpatterns = [
    path('',                ArticleListView.as_view(),   name='article_list'),
    path('create/',         ArticleCreateView.as_view(), name='article_create'),
    path('<slug:slug>/edit/', ArticleUpdateView.as_view(), name='article_edit'),
]
