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
        """Action pour désactiver les services sélectionnés."""
        updated_count = 0
        blocked_services = []
        
        for service in queryset:
            if service.actif:
                if service.can_be_deactivated():
                    service.actif = False
                    service.save()
                    updated_count += 1
                else:
                    blocked_services.append(f"{service.nom} (a des sous-services actifs)")
        
        if updated_count:
            messages.success(request, f'{updated_count} service(s) désactivé(s) avec succès.')
        
        if blocked_services:
            messages.warning(request, f'Impossible de désactiver: {", ".join(blocked_services)}')
        
        if not updated_count and not blocked_services:
            messages.info(request, 'Aucun service à désactiver (tous déjà inactifs).')
    desactiver_services.short_description = "Désactiver les services sélectionnés"
    
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