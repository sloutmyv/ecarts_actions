"""
Configuration de l'administration Django pour les services.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from ..models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Configuration de l'interface d'administration pour le modèle Service.
    """
    list_display = [
        'code', 'nom', 'actif', 'get_parent_display', 'get_niveau_display'
    ]
    list_filter = ['actif', 'parent']
    search_fields = ['nom', 'code']
    ordering = ['actif', 'nom']  # Services actifs en premier
    actions = ['activer_services', 'desactiver_services']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'parent')
        }),
        ('Configuration', {
            'fields': ('actif',),
            'description': 'Un service inactif reste dans l\'historique mais n\'apparaît plus dans les listes de sélection'
        }),
    )
    
    
    def get_parent_display(self, obj):
        """Affiche le service parent de manière lisible."""
        if obj.parent:
            return format_html(
                '<span style="color: #666;">{}</span>',
                f"{obj.parent.code} - {obj.parent.nom}"
            )
        return format_html('<em style="color: #999;">Service racine</em>')
    get_parent_display.short_description = 'Service parent'
    
    def get_niveau_display(self, obj):
        """Affiche le niveau hiérarchique avec indentation visuelle."""
        niveau = obj.get_niveau()
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * niveau
        return format_html(
            '{}Niveau {}',
            indent,
            niveau
        )
    get_niveau_display.short_description = 'Niveau hiérarchique'
    
    def activer_services(self, request, queryset):
        """Action pour activer les services sélectionnés."""
        updated_count = 0
        for service in queryset:
            if not service.actif:
                service.actif = True
                service.save()
                updated_count += 1
        
        if updated_count:
            messages.success(request, f'{updated_count} service(s) activé(s) avec succès.')
        else:
            messages.info(request, 'Aucun service à activer (tous déjà actifs).')
    activer_services.short_description = "Activer les services sélectionnés"
    
    def desactiver_services(self, request, queryset):
        """Action pour désactiver les services sélectionnés avec validation complète."""
        updated_count = 0
        blocked_services = []
        
        for service in queryset:
            if service.actif:
                if service.can_be_deactivated():
                    service.actif = False
                    service.save()
                    updated_count += 1
                else:
                    # Utiliser la méthode pour obtenir une raison détaillée
                    reason = service.get_deactivation_blocking_reason()
                    if reason:
                        blocked_services.append(f"{service.nom}: {reason}")
                    else:
                        blocked_services.append(f"{service.nom} (raison inconnue)")
        
        if updated_count:
            messages.success(request, f'{updated_count} service(s) désactivé(s) avec succès.')
        
        if blocked_services:
            error_msg = "Impossible de désactiver les services suivants:\n"
            for blocked in blocked_services:
                error_msg += f"• {blocked}\n"
            error_msg += "\nActions requises avant désactivation:"
            error_msg += "\n• Pour les utilisateurs: transférer vers un autre service ou les désactiver"  
            error_msg += "\n• Pour les écarts: transférer vers un autre service actif"
            error_msg += "\n• Pour les sous-services: les désactiver d'abord"
            messages.error(request, error_msg)
        
        if not updated_count and not blocked_services:
            messages.info(request, 'Aucun service à désactiver (tous déjà inactifs).')
    desactiver_services.short_description = "Désactiver les services sélectionnés"
    
    def save_model(self, request, obj, form, change):
        """
        Validation personnalisée avant sauvegarde.
        Empêche la désactivation d'un service avec des contraintes.
        """
        validation_failed = False
        
        if change and 'actif' in form.changed_data:
            # Si on essaie de passer le service à inactif
            if not obj.actif:
                if not obj.can_be_deactivated():
                    reason = obj.get_deactivation_blocking_reason()
                    messages.error(
                        request, 
                        f"Impossible de désactiver le service '{obj.nom}': {reason}\n\n"
                        f"Actions requises avant désactivation:\n"
                        f"• Pour les utilisateurs: transférer vers un autre service ou les désactiver\n"
                        f"• Pour les écarts: transférer vers un autre service actif\n"
                        f"• Pour les sous-services: les désactiver d'abord"
                    )
                    # Rétablir le statut actif
                    obj.actif = True
                    validation_failed = True
                    
        super().save_model(request, obj, form, change)
        
        # Si la validation a échoué, marquer la requête pour supprimer le message de succès
        if validation_failed:
            request._suppress_success_message = True

    def response_change(self, request, obj):
        """
        Personnalise la réponse après modification pour supprimer le message de succès
        si la validation a échoué.
        """
        response = super().response_change(request, obj)
        
        # Si on doit supprimer le message de succès
        if getattr(request, '_suppress_success_message', False):
            # Obtenir le stockage des messages
            storage = messages.get_messages(request)
            # Convertir en liste pour pouvoir la modifier
            messages_list = list(storage)
            # Filtrer pour enlever les messages de succès
            filtered_messages = [
                msg for msg in messages_list 
                if not (msg.level == messages.SUCCESS and "modifié avec succès" in str(msg))
            ]
            
            # Vider le stockage et remettre seulement les messages filtrés
            storage._queued_messages.clear()
            for msg in filtered_messages:
                storage.add(msg.level, msg.message, msg.extra_tags)
        
        return response
    
    def delete_model(self, request, obj):
        """
        Validation personnalisée avant suppression.
        Empêche la suppression d'un service avec des contraintes actives.
        """
        if not obj.can_be_deleted():
            reason = obj.get_deletion_blocking_reason()
            messages.error(
                request,
                f"Impossible de supprimer le service '{obj.nom}': {reason}\n\n"
                f"Vous devez d'abord résoudre ces contraintes avant de pouvoir supprimer le service. "
                f"Pour les rôles de validateur, utilisez la <a href='/workflow/'>gestion du workflow</a>."
            )
            # Marquer que la suppression a été bloquée
            request._suppress_delete_success_message = True
            return  # Annuler la suppression
        
        # Si toutes les vérifications passent, procéder à la suppression
        super().delete_model(request, obj)

    def response_delete(self, request, obj_display, obj_id):
        """
        Personnalise la réponse après suppression pour supprimer le message de succès
        si la suppression a été bloquée.
        """
        # Si la suppression a été bloquée, supprimer le message de succès
        if getattr(request, '_suppress_delete_success_message', False):
            # Obtenir le stockage des messages
            storage = messages.get_messages(request)
            # Convertir en liste pour pouvoir la modifier
            messages_list = list(storage)
            # Filtrer pour enlever les messages de succès de suppression
            filtered_messages = [
                msg for msg in messages_list 
                if not (msg.level == messages.SUCCESS and "supprimé avec succès" in str(msg))
            ]
            
            # Vider le stockage et remettre seulement les messages filtrés
            storage._queued_messages.clear()
            for msg in filtered_messages:
                storage.add(msg.level, msg.message, msg.extra_tags)
            
            # Rediriger vers la liste au lieu de la page de confirmation de suppression
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist'))
        
        return super().response_delete(request, obj_display, obj_id)
    
    def delete_queryset(self, request, queryset):
        """
        Validation personnalisée pour suppression en lot.
        Empêche la suppression des services avec des contraintes.
        """
        blocked_services = []
        deletable_services = []
        
        for service in queryset:
            if service.can_be_deleted():
                deletable_services.append(service)
            else:
                reason = service.get_deletion_blocking_reason()
                blocked_services.append(f"{service.nom}: {reason}")
        
        # Afficher les messages d'information
        
        # Supprimer seulement les services sans contraintes
        if deletable_services:
            deleted_count = len(deletable_services)
            for service in deletable_services:
                service.delete()
            messages.success(request, f'{deleted_count} service(s) supprimé(s) avec succès.')
        
        # Afficher les services bloqués
        if blocked_services:
            error_msg = "Impossible de supprimer les services suivants:\n"
            for blocked in blocked_services:
                error_msg += f"• {blocked}\n"
            error_msg += "\nActions requises avant suppression:"
            error_msg += "\n• Transférer ou désactiver les utilisateurs associés"
            error_msg += "\n• Transférer les écarts vers d'autres services actifs"
            error_msg += "\n• Supprimer ou déplacer les sous-services"
            messages.error(request, error_msg)
    
    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les relations parent."""
        return super().get_queryset(request).select_related('parent')
    
    def changelist_view(self, request, extra_context=None):
        """Ajoute le contexte pour les boutons import/export."""
        extra_context = extra_context or {}
        extra_context['has_import_export'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    class Media:
        css = {
            'all': ('css/admin_service.css',)  # Pour le style personnalisé si nécessaire
        }