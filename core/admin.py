from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'nom', 'get_parent_display', 'get_niveau_display'
    ]
    list_filter = ['parent']
    search_fields = ['nom', 'code']
    ordering = ['nom']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'parent')
        }),
    )
    
    def get_parent_display(self, obj):
        if obj.parent:
            return format_html(
                '<span style="color: #666;">{}</span>',
                f"{obj.parent.code} - {obj.parent.nom}"
            )
        return format_html('<em style="color: #999;">Service racine</em>')
    get_parent_display.short_description = 'Service parent'
    
    def get_niveau_display(self, obj):
        niveau = obj.get_niveau()
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * niveau
        return format_html(
            '{}Niveau {}',
            indent,
            niveau
        )
    get_niveau_display.short_description = 'Niveau hiérarchique'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')
    
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_import_export'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    class Media:
        css = {
            'all': ('css/admin_service.css',)  # Pour le style personnalisé si nécessaire
        }
