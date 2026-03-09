from django.urls import path
from .views import FAQListView, FAQCreateView, FAQUpdateView

urlpatterns = [
    path('',                FAQListView.as_view(),   name='faq_list'),
    path('create/',         FAQCreateView.as_view(), name='faq_create'),
    path('<int:pk>/edit/', FAQUpdateView.as_view(), name='faq_edit'),
]
