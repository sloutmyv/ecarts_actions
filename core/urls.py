from django.urls import path
from . import views
from .views import auth

urlpatterns = [
    # URLs d'authentification
    path('login/', auth.custom_login, name='login'),
    path('logout/', auth.custom_logout, name='logout'),
    path('change-password/', auth.change_password, name='change_password'),
    
    path('', views.dashboard, name='dashboard'),
    
    # URLs pour la gestion des services
    path('services/', views.services_list, name='services_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    
    # URLs pour import/export JSON des services
    path('services/export-json/', views.export_services_json, name='export_services_json'),
    path('services/import-json/', views.import_services_json, name='import_services_json'),
    path('services/import-form/', views.import_services_form, name='import_services_form'),
    
    # URLs pour la gestion des utilisateurs
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/reset-password/', views.user_reset_password, name='user_reset_password'),
    
    # URLs pour export JSON des utilisateurs
    path('users/export-json/', views.export_users_json, name='export_users_json'),
]