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
        'code', 'nom', 'get_actif_display', 'get_parent_display', 'get_niveau_display'
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
    
    def get_actif_display(self, obj):
        """Affiche le statut actif avec badge coloré."""
        if obj.actif:
            return format_html(
                '<span style="background: #d4edda; color: #155724; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ ACTIF</span>'
            )
        else:
            return format_html(
                '<span style="background: #f8d7da; color: #721c24; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✗ INACTIF</span>'
            )
    get_actif_display.short_description = 'Statut'
    
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
                    
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """
        Validation personnalisée avant suppression.
        Empêche la suppression d'un service avec des utilisateurs actifs associés.
        """
        from ..models.users import User
        from ..models.gaps import GapReport
        
        # Vérifier les utilisateurs actifs associés
        active_users_count = User.objects.filter(service=obj, actif=True).count()
        if active_users_count > 0:
            messages.error(
                request,
                f"Impossible de supprimer le service '{obj.nom}': "
                f"il a {active_users_count} utilisateur(s) actif(s) associé(s).\n\n"
                f"Vous devez d'abord transférer ces utilisateurs vers un autre service "
                f"ou les désactiver avant de pouvoir supprimer le service."
            )
            return  # Annuler la suppression
        
        # Vérifier les déclarations d'écarts associées
        gap_reports_count = GapReport.objects.filter(service=obj).count()
        if gap_reports_count > 0:
            messages.error(
                request,
                f"Impossible de supprimer le service '{obj.nom}': "
                f"il est associé à {gap_reports_count} déclaration(s) d'écart(s).\n\n"
                f"Vous devez d'abord transférer ces écarts vers un autre service actif "
                f"avant de pouvoir supprimer le service."
            )
            return  # Annuler la suppression
        
        # Vérifier les sous-services
        if obj.sous_services.exists():
            children_count = obj.sous_services.count()
            messages.error(
                request,
                f"Impossible de supprimer le service '{obj.nom}': "
                f"il contient {children_count} sous-service(s).\n\n"
                f"Vous devez d'abord supprimer ou déplacer tous les sous-services."
            )
            return  # Annuler la suppression
        
        # Si toutes les vérifications passent, procéder à la suppression
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """
        Validation personnalisée pour suppression en lot.
        Empêche la suppression des services avec des contraintes.
        """
        from ..models.users import User
        from ..models.gaps import GapReport
        
        blocked_services = []
        deletable_services = []
        
        for service in queryset:
            reasons = []
            
            # Vérifier les utilisateurs actifs
            active_users_count = User.objects.filter(service=service, actif=True).count()
            if active_users_count > 0:
                reasons.append(f"{active_users_count} utilisateur(s) actif(s)")
            
            # Vérifier les écarts
            gap_reports_count = GapReport.objects.filter(service=service).count()
            if gap_reports_count > 0:
                reasons.append(f"{gap_reports_count} déclaration(s) d'écart(s)")
            
            # Vérifier les sous-services
            if service.sous_services.exists():
                children_count = service.sous_services.count()
                reasons.append(f"{children_count} sous-service(s)")
            
            if reasons:
                blocked_services.append(f"{service.nom}: {', '.join(reasons)}")
            else:
                deletable_services.append(service)
        
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