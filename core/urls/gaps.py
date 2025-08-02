"""
URLs pour la gestion des écarts.
"""
from django.urls import path
from core.views import gaps

app_name = 'gaps'

urlpatterns = [
    # Liste des écarts individuels (page principale)
    path('', gaps.gap_list, name='gap_list'),
    
    # Déclarations d'écart
    path('declarations/', gaps.gap_report_list, name='gap_report_list'),
    path('declaration/<int:pk>/', gaps.gap_report_detail, name='gap_report_detail'),
    path('declaration/new/', gaps.gap_report_create, name='gap_report_create'),
    path('declaration/<int:pk>/edit/', gaps.gap_report_edit, name='gap_report_edit'),
    
    # Écarts individuels
    path('declaration/<int:gap_report_pk>/gap/new/', gaps.gap_create, name='gap_create'),
    path('gap/<int:pk>/edit/', gaps.gap_edit, name='gap_edit'),
    
    # API HTMX
    path('api/gap-types/', gaps.get_gap_types, name='get_gap_types'),
    path('api/process-field/', gaps.get_process_field, name='get_process_field'),
]