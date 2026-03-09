from django.urls import path
from .views import SocialListView, SocialCreateView, SocialUpdateView

urlpatterns = [
    path('',                  SocialListView.as_view(),   name='social_list'),
    path('create/',           SocialCreateView.as_view(), name='social_create'),
    path('<int:pk>/edit/', SocialUpdateView.as_view(), name='social_edit'),
]
