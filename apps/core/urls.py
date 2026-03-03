from django.urls import path
from . import views

urlpatterns = [
    path('audit/',       views.AuditLogView.as_view(), name='audit_log'),
    path('audit/clear/', views.clear_audit_log,        name='clear_audit_log'),

    # Generic action endpoints
    path('toggle/<str:model_key>/<int:pk>/',  views.toggle_status, name='toggle_status'),
    path('delete/<str:model_key>/<int:pk>/',  views.delete_object,  name='delete_object'),
    path('bulk/<str:model_key>/',             views.bulk_action,    name='bulk_action'),
    path('sort/<str:model_key>/',             views.update_order,   name='update_order'),
    path('slug/<str:model_key>/',             views.ajax_check_slug, name='check_slug'),
]
