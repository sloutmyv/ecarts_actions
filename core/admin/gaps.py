"""
Configuration de l'interface d'administration pour les modèles de gestion des écarts.
"""
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from core.models import AuditSource, Process, GapType, GapReport, Gap


@admin.register(AuditSource)
class AuditSourceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'requires_process', 'is_active', 'created_at']
    list_filter = ['requires_process', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'description']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description')
        }),
        ('Configuration', {
            'fields': ('requires_process', 'is_active')
        }),
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '50'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 50})},
    }


# Le modèle Department est remplacé par le modèle Service existant


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name', 'description']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description')
        }),
        ('Configuration', {
            'fields': ('is_active',)
        }),
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '50'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 50})},
    }


@admin.register(GapType)
class GapTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'audit_source', 'is_active', 'created_at']
    list_filter = ['audit_source', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'description', 'audit_source__name']
    ordering = ['audit_source__name', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'audit_source', 'description')
        }),
        ('Configuration', {
            'fields': ('is_active',)
        }),
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '50'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 50})},
    }


class GapInline(admin.TabularInline):
    """
    Inline pour afficher les écarts dans l'admin des déclarations.
    """
    model = Gap
    extra = 1
    fields = ['gap_number', 'gap_type', 'description', 'status']
    readonly_fields = ['gap_number']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('gap_type')


@admin.register(GapReport)
class GapReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'audit_source', 'service', 'observation_date', 'declared_by', 'created_at']
    list_filter = ['audit_source', 'service', 'observation_date', 'created_at']
    search_fields = ['source_reference', 'location', 'declared_by__username', 'declared_by__first_name', 'declared_by__last_name']
    ordering = ['-observation_date', '-created_at']
    date_hierarchy = 'observation_date'
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('audit_source', 'source_reference', 'service', 'process')
        }),
        ('Localisation et dates', {
            'fields': ('location', 'observation_date')
        }),
        ('Personnes impliquées', {
            'fields': ('declared_by', 'involved_users')
        }),
    )
    
    filter_horizontal = ('involved_users',)
    inlines = [GapInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'audit_source', 'service', 'process', 'declared_by'
        ).prefetch_related('involved_users')
    
    def save_model(self, request, obj, form, change):
        """
        Assigne automatiquement l'utilisateur connecté comme déclarant si non défini.
        """
        if not obj.declared_by:
            obj.declared_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Gap)
class GapAdmin(admin.ModelAdmin):
    list_display = ['gap_number', 'gap_type', 'gap_report', 'status', 'created_at']
    list_filter = ['status', 'gap_type__audit_source', 'created_at']
    search_fields = ['gap_number', 'description', 'gap_type__name']
    ordering = ['-created_at']
    readonly_fields = ['gap_number']
    
    fieldsets = (
        ('Identification', {
            'fields': ('gap_number', 'gap_report', 'gap_type')
        }),
        ('Détails', {
            'fields': ('description', 'status')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'gap_report', 'gap_type', 'gap_type__audit_source'
        )
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 50})},
    }