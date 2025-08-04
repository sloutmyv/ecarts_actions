"""
Configuration de l'interface d'administration pour les modèles de gestion des écarts.
"""
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from core.models import AuditSource, Process, GapType, GapReport, Gap, GapReportAttachment, GapAttachment


@admin.register(AuditSource)
class AuditSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'requires_process', 'created_at']
    list_filter = ['requires_process', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Configuration', {
            'fields': ('requires_process',)
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
    list_display = ['name', 'audit_source', 'created_at']
    list_filter = ['audit_source', 'created_at']
    search_fields = ['name', 'description', 'audit_source__name']
    ordering = ['audit_source__name', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'audit_source', 'description')
        }),
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '50'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 50})},
    }


class GapReportAttachmentInline(admin.TabularInline):
    """
    Inline pour afficher les pièces jointes dans l'admin des déclarations.
    """
    model = GapReportAttachment
    extra = 0
    fields = ['name', 'file', 'uploaded_by', 'created_at']
    readonly_fields = ['uploaded_by', 'created_at']
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


class GapAttachmentInline(admin.TabularInline):
    """
    Inline pour afficher les pièces jointes dans l'admin des écarts.
    """
    model = GapAttachment
    extra = 0
    fields = ['name', 'file', 'uploaded_by', 'created_at']
    readonly_fields = ['uploaded_by', 'created_at']
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


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
    search_fields = ['source_reference', 'location', 'declared_by__matricule', 'declared_by__nom', 'declared_by__prenom']
    ordering = ['-observation_date', '-created_at']
    date_hierarchy = 'observation_date'
    
    fieldsets = (
        ('Personnes impliquées (QUI?)', {
            'fields': ('declared_by', 'involved_users')
        }),
        ('Dates (QUAND?)', {
            'fields': ('observation_date', 'created_at')
        }),
        ('Localisation (OÙ?)', {
            'fields': ('service', 'location')
        }),
        ('Informations principales', {
            'fields': ('audit_source', 'source_reference', 'process')
        }),
    )
    
    filter_horizontal = ('involved_users',)
    readonly_fields = ('created_at',)
    inlines = [GapReportAttachmentInline, GapInline]
    
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
    
    inlines = [GapAttachmentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'gap_report', 'gap_type', 'gap_type__audit_source'
        )
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 50})},
    }


@admin.register(GapReportAttachment)
class GapReportAttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'gap_report', 'file_size_mb', 'uploaded_by', 'created_at']
    list_filter = ['created_at', 'uploaded_by']
    search_fields = ['name', 'gap_report__id', 'uploaded_by__matricule']
    ordering = ['-created_at']
    readonly_fields = ('file_size_mb', 'file_extension', 'uploaded_by', 'created_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'gap_report', 'file')
        }),
        ('Métadonnées', {
            'fields': ('file_size_mb', 'file_extension', 'uploaded_by', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('gap_report', 'uploaded_by')
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GapAttachment)
class GapAttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'gap', 'file_size_mb', 'uploaded_by', 'created_at']
    list_filter = ['created_at', 'uploaded_by']
    search_fields = ['name', 'gap__gap_number', 'uploaded_by__matricule']
    ordering = ['-created_at']
    readonly_fields = ('file_size_mb', 'file_extension', 'uploaded_by', 'created_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'gap', 'file')
        }),
        ('Métadonnées', {
            'fields': ('file_size_mb', 'file_extension', 'uploaded_by', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('gap', 'uploaded_by')
    
    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)