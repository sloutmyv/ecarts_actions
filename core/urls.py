from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # URLs pour la gestion des services
    path('services/', views.services_list, name='services_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    
    # URLs pour import/export JSON
    path('services/export-json/', views.export_services_json, name='export_services_json'),
    path('services/import-json/', views.import_services_json, name='import_services_json'),
    path('services/import-form/', views.import_services_form, name='import_services_form'),
]