from django.urls import path
from . import views

urlpatterns = [
    path('upload/',  views.MediaUploadView.as_view(),  name='media_upload'),
    path('library/', views.MediaLibraryView.as_view(), name='media_library'),
]
