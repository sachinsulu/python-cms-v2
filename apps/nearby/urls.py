from django.urls import path
from .views import NearbyListView, NearbyCreateView, NearbyUpdateView

urlpatterns = [
    path('',                NearbyListView.as_view(),   name='nearby_list'),
    path('create/',         NearbyCreateView.as_view(), name='nearby_create'),
    path('<slug:slug>/edit/', NearbyUpdateView.as_view(), name='nearby_edit'),
]
