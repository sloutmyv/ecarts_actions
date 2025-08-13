"""
Configuration de l'interface d'administration pour les notifications et validations.
"""
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from core.models import Notification, GapValidation


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    change_list_template = "admin/notifications/notification_change_list.html"
    list_display = ['title', 'user', 'gap', 'type', 'priority', 'is_read', 'created_at']
    list_filter = ['type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__matricule', 'user__nom', 'user__prenom', 'gap__gap_number']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ('read_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Destinataire', {
            'fields': ('user', 'gap')
        }),
        ('Contenu', {
            'fields': ('type', 'title', 'message', 'priority')
        }),
        ('État', {
            'fields': ('is_read', 'read_at')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'gap', 'gap__gap_type', 'gap__gap_report'
        )
    
    def has_add_permission(self, request):
        """Empêcher la création manuelle de notifications"""
        return False
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete_all/', self.delete_all_view, name='notification_delete_all'),
        ]
        return custom_urls + urls
    
    def delete_all_view(self, request):
        """Vue personnalisée pour supprimer toutes les notifications"""
        if request.POST.get('confirm'):
            # Compter par type avant suppression
            total_count = Notification.objects.count()
            if total_count == 0:
                self.message_user(
                    request, 
                    "ℹ️ Aucune notification à supprimer.",
                    level=messages.INFO
                )
                return HttpResponseRedirect(reverse('admin:core_notification_changelist'))
            
            type_counts = {}
            for choice in Notification.TYPE_CHOICES:
                type_key, type_label = choice
                count = Notification.objects.filter(type=type_key).count()
                if count > 0:
                    type_counts[type_label] = count
            
            # Suppression effective
            deleted_count, _ = Notification.objects.all().delete()
            
            # Message de confirmation
            details = ", ".join([f"{count} {type_name}" for type_name, count in type_counts.items()])
            self.message_user(
                request, 
                f"✅ {deleted_count} notifications supprimées avec succès ! Détails : {details}",
                level=messages.SUCCESS
            )
            
            # Log simple dans les messages Django
            import logging
            logger = logging.getLogger('django.admin')
            logger.info(f"SUPPRESSION MASSIVE - {deleted_count} notifications supprimées par {request.user}")
            
            return HttpResponseRedirect(reverse('admin:core_notification_changelist'))
        
        # Page de confirmation
        total_count = Notification.objects.count()
        if total_count == 0:
            self.message_user(
                request, 
                "ℹ️ Aucune notification à supprimer.",
                level=messages.INFO
            )
            return HttpResponseRedirect(reverse('admin:core_notification_changelist'))
        
        # Statistiques par type
        type_stats = []
        for choice in Notification.TYPE_CHOICES:
            type_key, type_label = choice
            count = Notification.objects.filter(type=type_key).count()
            if count > 0:
                type_stats.append({
                    'type': type_label,
                    'count': count
                })
        
        context = {
            'title': 'Confirmer la suppression de TOUTES les notifications',
            'total_count': total_count,
            'type_stats': type_stats,
            'action_name': 'Supprimer toutes les notifications',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        
        return render(request, 'admin/notifications/delete_all_confirmation.html', context)
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_all_notifications']
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{count} notification(s) marquée(s) comme lue(s).")
    mark_as_read.short_description = "Marquer comme lu"
    
    def mark_as_unread(self, request, queryset):
        count = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f"{count} notification(s) marquée(s) comme non lue(s).")
    mark_as_unread.short_description = "Marquer comme non lu"
    
    def delete_all_notifications(self, request, queryset):
        """Supprimer TOUTES les notifications (pas seulement celles sélectionnées)"""
        
        if request.POST.get('confirm'):
            # Compter par type avant suppression
            total_count = Notification.objects.count()
            type_counts = {}
            for choice in Notification.TYPE_CHOICES:
                type_key, type_label = choice
                count = Notification.objects.filter(type=type_key).count()
                if count > 0:
                    type_counts[type_label] = count
            
            # Suppression effective
            deleted_count, _ = Notification.objects.all().delete()
            
            # Message de confirmation
            details = ", ".join([f"{count} {type_name}" for type_name, count in type_counts.items()])
            self.message_user(
                request, 
                f"✅ {deleted_count} notifications supprimées avec succès ! Détails : {details}",
                level=messages.SUCCESS
            )
            
            # Log de l'action
            import logging
            logger = logging.getLogger('django.admin')
            logger.info(f"""SUPPRESSION EN MASSE - TOUTES LES NOTIFICATIONS
            Total supprimé : {deleted_count} notifications
            Détails par type : {details}
            Effectué par : {request.user.get_full_name() or request.user.matricule}""")
            
            return HttpResponseRedirect(reverse('admin:core_notification_changelist'))
        
        # Page de confirmation
        total_count = Notification.objects.count()
        if total_count == 0:
            self.message_user(
                request, 
                "ℹ️ Aucune notification à supprimer.",
                level=messages.INFO
            )
            return HttpResponseRedirect(reverse('admin:core_notification_changelist'))
        
        # Statistiques par type
        type_stats = []
        for choice in Notification.TYPE_CHOICES:
            type_key, type_label = choice
            count = Notification.objects.filter(type=type_key).count()
            if count > 0:
                type_stats.append({
                    'type': type_label,
                    'count': count
                })
        
        context = {
            'title': 'Confirmer la suppression de TOUTES les notifications',
            'total_count': total_count,
            'type_stats': type_stats,
            'action_name': 'Supprimer toutes les notifications',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        
        return render(request, 'admin/notifications/delete_all_confirmation.html', context)
    
    delete_all_notifications.short_description = "🗑️ SUPPRIMER TOUTES LES NOTIFICATIONS"


@admin.register(GapValidation)
class GapValidationAdmin(admin.ModelAdmin):
    list_display = ['gap', 'validator', 'level', 'action', 'created_at']
    list_filter = ['action', 'level', 'created_at']
    search_fields = ['gap__gap_number', 'validator__matricule', 'validator__nom', 'validator__prenom', 'comment']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ('gap', 'validator', 'level', 'action', 'comment', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Validation', {
            'fields': ('gap', 'validator', 'level', 'action')
        }),
        ('Détails', {
            'fields': ('comment',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'gap', 'gap__gap_type', 'gap__gap_report', 'validator'
        )
    
    def has_add_permission(self, request):
        # Empêcher la création manuelle de validations
        return False
    
    def has_change_permission(self, request, obj=None):
        # Empêcher la modification de validations (lecture seule)
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Permettre la suppression pour le nettoyage des données
        return request.user.is_superuser
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 50})},
    }