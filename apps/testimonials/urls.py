from django.urls import path
from .views import TestimonialListView, TestimonialCreateView, TestimonialUpdateView

urlpatterns = [
    path('',                         TestimonialListView.as_view(),   name='testimonial_list'),
    path('create/',                  TestimonialCreateView.as_view(), name='testimonial_create'),
    path('<slug:slug>/edit/',         TestimonialUpdateView.as_view(), name='testimonial_edit'),
]
