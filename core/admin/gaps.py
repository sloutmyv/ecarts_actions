"""
Configuration de l'interface d'administration pour les modèles de gestion des écarts.
"""
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from core.models import AuditSource, Process, GapType, GapReport, Gap, GapReportAttachment, GapAttachment, HistoriqueModification


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
    list_display = ['name', 'audit_source', 'is_gap', 'created_at']
    list_filter = ['audit_source', 'is_gap', 'created_at']
    search_fields = ['name', 'description', 'audit_source__name']
    ordering = ['audit_source__name', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'audit_source', 'description')
        }),
        ('Configuration', {
            'fields': ('is_gap',)
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
    list_display = ['gap_number', 'gap_type', 'gap_report', 'status', 'attachments_count', 'notifications_count', 'validations_count', 'created_at']
    list_filter = ['status', 'gap_type__audit_source', 'created_at']
    search_fields = ['gap_number', 'description', 'gap_type__name']
    ordering = ['-created_at']
    readonly_fields = ['gap_number', 'attachments_count', 'notifications_count', 'validations_count']
    
    fieldsets = (
        ('Identification', {
            'fields': ('gap_number', 'gap_report', 'gap_type')
        }),
        ('Détails', {
            'fields': ('description', 'status')
        }),
        ('Éléments liés', {
            'fields': ('attachments_count', 'notifications_count', 'validations_count'),
            'description': 'Ces éléments seront automatiquement supprimés avec cet événement.'
        }),
    )
    
    inlines = [GapAttachmentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'gap_report', 'gap_type', 'gap_type__audit_source'
        ).prefetch_related(
            'attachments', 'notifications', 'validations'
        )
    
    def attachments_count(self, obj):
        """Nombre de pièces jointes"""
        count = obj.attachments.count()
        return f"{count} pièce(s) jointe(s)" if count > 0 else "Aucune pièce jointe"
    attachments_count.short_description = "Pièces jointes"
    
    def notifications_count(self, obj):
        """Nombre de notifications"""
        count = obj.notifications.count()
        return f"{count} notification(s)" if count > 0 else "Aucune notification"
    notifications_count.short_description = "Notifications"
    
    def validations_count(self, obj):
        """Nombre de validations"""
        count = obj.validations.count()
        return f"{count} validation(s)" if count > 0 else "Aucune validation"
    validations_count.short_description = "Validations"
    
    def delete_model(self, request, obj):
        """Suppression personnalisée avec log"""
        # Compter les éléments qui seront supprimés
        attachments_count = obj.attachments.count()
        notifications_count = obj.notifications.count()
        validations_count = obj.validations.count()
        
        # Log de la suppression
        self.log_deletion(request, obj, f"""
        Suppression de l'événement {obj.gap_number} :
        - {attachments_count} pièce(s) jointe(s)
        - {notifications_count} notification(s)
        - {validations_count} validation(s)
        - 1 entrée d'historique sera créée automatiquement
        """)
        
        # Suppression normale (cascade automatique)
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Suppression en lot personnalisée avec log"""
        total_attachments = sum(gap.attachments.count() for gap in queryset)
        total_notifications = sum(gap.notifications.count() for gap in queryset)
        total_validations = sum(gap.validations.count() for gap in queryset)
        
        gap_numbers = [gap.gap_number for gap in queryset]
        
        self.log_deletion(request, None, f"""
        Suppression en lot de {len(gap_numbers)} événements :
        Événements : {', '.join(gap_numbers)}
        - {total_attachments} pièce(s) jointe(s)
        - {total_notifications} notification(s)
        - {total_validations} validation(s)
        - {len(gap_numbers)} entrée(s) d'historique seront créées automatiquement
        """)
        
        # Suppression normale (cascade automatique)
        super().delete_queryset(request, queryset)
    
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


@admin.register(HistoriqueModification)
class HistoriqueModificationAdmin(admin.ModelAdmin):
    change_list_template = "admin/historique/historique_change_list.html"
    list_display = ['objet_repr', 'action', 'utilisateur', 'created_at', 'objet_type']
    list_filter = ['action', 'objet_type', 'created_at', 'utilisateur']
    search_fields = ['description', 'objet_repr', 'utilisateur__matricule', 'utilisateur__nom', 'utilisateur__prenom']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ('gap_report', 'gap', 'action', 'objet_type', 'objet_id', 'objet_repr', 'utilisateur', 'created_at', 'donnees_avant', 'donnees_apres')
    
    fieldsets = (
        ('Objet modifié', {
            'fields': ('objet_type', 'objet_repr', 'gap_report', 'gap')
        }),
        ('Action', {
            'fields': ('action', 'description', 'utilisateur', 'created_at')
        }),
        ('Détails techniques', {
            'fields': ('donnees_avant', 'donnees_apres'),
            'classes': ('collapse',)  # Section repliable par défaut
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'utilisateur', 'gap_report', 'gap', 'gap__gap_type'
        )
    
    def has_add_permission(self, request):
        # Empêcher la création manuelle d'historiques
        return False
    
    def has_change_permission(self, request, obj=None):
        # Empêcher la modification d'historiques (lecture seule)
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Permettre la suppression pour le nettoyage des données
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        # Empêcher la création manuelle d'historiques
        return False
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete_all/', self.delete_all_historique_view, name='historique_delete_all'),
        ]
        return custom_urls + urls
    
    def delete_all_historique_view(self, request):
        """Vue personnalisée pour supprimer tout l'historique"""
        if request.POST.get('confirm'):
            # Compter par type d'action avant suppression
            total_count = HistoriqueModification.objects.count()
            if total_count == 0:
                self.message_user(
                    request, 
                    "ℹ️ Aucun historique à supprimer.",
                    level=messages.INFO
                )
                return HttpResponseRedirect(reverse('admin:core_historiquemodification_changelist'))
            
            action_counts = {}
            for action in HistoriqueModification.objects.values_list('action', flat=True).distinct():
                count = HistoriqueModification.objects.filter(action=action).count()
                if count > 0:
                    action_counts[action] = count
            
            # Suppression effective
            deleted_count, _ = HistoriqueModification.objects.all().delete()
            
            # Message de confirmation
            details = ", ".join([f"{count} {action}" for action, count in action_counts.items()])
            self.message_user(
                request, 
                f"✅ {deleted_count} entrées d'historique supprimées avec succès ! Détails : {details}",
                level=messages.SUCCESS
            )
            
            # Log simple dans les messages Django
            import logging
            logger = logging.getLogger('django.admin')
            logger.info(f"SUPPRESSION MASSIVE - {deleted_count} entrées d'historique supprimées par {request.user}")
            
            return HttpResponseRedirect(reverse('admin:core_historiquemodification_changelist'))
        
        # Page de confirmation
        total_count = HistoriqueModification.objects.count()
        if total_count == 0:
            self.message_user(
                request, 
                "ℹ️ Aucun historique à supprimer.",
                level=messages.INFO
            )
            return HttpResponseRedirect(reverse('admin:core_historiquemodification_changelist'))
        
        # Statistiques par action
        action_stats = []
        for action in HistoriqueModification.objects.values_list('action', flat=True).distinct():
            count = HistoriqueModification.objects.filter(action=action).count()
            if count > 0:
                action_stats.append({
                    'action': action,
                    'count': count
                })
        
        context = {
            'title': 'Confirmer la suppression de TOUT l\'historique',
            'total_count': total_count,
            'action_stats': action_stats,
            'action_name': 'Supprimer tout l\'historique',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        
        return render(request, 'admin/historique/delete_all_confirmation.html', context)