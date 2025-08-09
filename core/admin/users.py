"""
Configuration de l'administration Django pour les utilisateurs.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuration de l'administration pour le modèle User personnalisé.
    """
    
    # Affichage dans la liste
    list_display = (
        'matricule', 'get_full_name', 'email', 'get_actif_display', 'droits_badge', 'service_link', 
        'must_change_password', 'created_at'
    )
    list_filter = ('actif', 'droits', 'must_change_password', 'service', 'created_at')
    search_fields = ('matricule', 'nom', 'prenom', 'email')
    ordering = ('-actif', 'nom', 'prenom')  # Utilisateurs actifs en premier
    actions = ['activer_utilisateurs', 'desactiver_utilisateurs']
    
    # Affichage détaillé
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('matricule', 'nom', 'prenom', 'email')
        }),
        ('Droits et permissions', {
            'fields': ('droits', 'service', 'actif', 'is_staff', 'is_superuser')
        }),
        ('Mot de passe', {
            'fields': ('password', 'must_change_password')
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Formulaire d'ajout (sans mot de passe - sera défini automatiquement)
    add_fieldsets = (
        ('Informations obligatoires', {
            'classes': ('wide',),
            'fields': ('matricule', 'nom', 'prenom')
        }),
        ('Informations optionnelles', {
            'fields': ('email', 'droits', 'service', 'actif')
        }),
        ('Mot de passe', {
            'description': 'Le mot de passe sera automatiquement défini à "azerty" et devra être changé lors de la première connexion.',
            'classes': ('collapse',),
            'fields': ()
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    # Filtres personnalisés
    list_per_page = 25
    
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
    get_actif_display.admin_order_field = 'actif'
    
    def droits_badge(self, obj):
        """Affiche un badge coloré pour les droits."""
        colors = {
            'SA': 'background-color: #dc2626; color: white;',  # Rouge pour Super Admin
            'AD': 'background-color: #2563eb; color: white;',  # Bleu pour Admin
            'US': 'background-color: #16a34a; color: white;',  # Vert pour User
        }
        style = colors.get(obj.droits, 'background-color: #6b7280; color: white;')
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; {}">{}</span>',
            style,
            obj.get_droits_display()
        )
    droits_badge.short_description = 'Droits'
    droits_badge.admin_order_field = 'droits'
    
    def service_link(self, obj):
        """Affiche un lien vers le service si défini."""
        if obj.service:
            url = reverse('admin:core_service_change', args=[obj.service.pk])
            return format_html('<a href="{}">{}</a>', url, obj.service.nom)
        return format_html('<span style="color: #6b7280; font-style: italic;">Aucun service</span>')
    service_link.short_description = 'Service'
    service_link.admin_order_field = 'service__nom'
    
    def activer_utilisateurs(self, request, queryset):
        """Action pour activer les utilisateurs sélectionnés."""
        updated_count = 0
        for user in queryset:
            if not user.actif:
                user.actif = True
                user.save()
                updated_count += 1
        
        if updated_count:
            messages.success(request, f'{updated_count} utilisateur(s) activé(s) avec succès.')
        else:
            messages.info(request, 'Aucun utilisateur à activer (tous déjà actifs).')
    activer_utilisateurs.short_description = "Activer les utilisateurs sélectionnés"
    
    def desactiver_utilisateurs(self, request, queryset):
        """Action pour désactiver les utilisateurs sélectionnés."""
        updated_count = 0
        blocked_users = []
        
        for user in queryset:
            if user.actif:
                # Empêcher la désactivation de son propre compte
                if user == request.user:
                    blocked_users.append(f"{user.get_full_name()} (votre propre compte)")
                else:
                    user.actif = False
                    user.save()
                    updated_count += 1
        
        if updated_count:
            messages.success(request, f'{updated_count} utilisateur(s) désactivé(s) avec succès.')
        
        if blocked_users:
            messages.warning(request, f'Impossible de désactiver: {", ".join(blocked_users)}')
        
        if not updated_count and not blocked_users:
            messages.info(request, 'Aucun utilisateur à désactiver (tous déjà inactifs).')
    desactiver_utilisateurs.short_description = "Désactiver les utilisateurs sélectionnés"
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related."""
        return super().get_queryset(request).select_related('service')
    
    def save_model(self, request, obj, form, change):
        """Logique de sauvegarde personnalisée."""
        # Si c'est un nouvel utilisateur et qu'aucun mot de passe n'est défini
        if not change and not obj.password:
            obj.set_password('azerty')
            obj.must_change_password = True
        
        super().save_model(request, obj, form, change)
    
    def changelist_view(self, request, extra_context=None):
        """Ajoute le contexte pour les boutons import/export."""
        extra_context = extra_context or {}
        extra_context['has_import_export'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        """Personnalise le formulaire selon l'utilisateur connecté."""
        form = super().get_form(request, obj, **kwargs)
        
        # Empêcher les utilisateurs non super-admin de modifier certains champs
        if not request.user.is_superuser:
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'droits' in form.base_fields:
                # Limiter les choix de droits
                choices = form.base_fields['droits'].choices
                if request.user.droits != 'SA':  # Si pas Super Admin
                    # Enlever le choix Super Admin
                    form.base_fields['droits'].choices = [
                        choice for choice in choices if choice[0] != 'SA'
                    ]
        
        return form
    
    def has_delete_permission(self, request, obj=None):
        """Empêche la suppression de son propre compte."""
        if obj and obj == request.user:
            return False
        return super().has_delete_permission(request, obj)
    
    def has_change_permission(self, request, obj=None):
        """Vérifie les permissions de modification."""
        # Super admin peut tout modifier
        if request.user.is_superuser:
            return True
        
        # Admin peut modifier mais pas les super admins
        if hasattr(request.user, 'droits') and request.user.droits == 'AD':
            if obj and obj.droits == 'SA':
                return False
            return True
        
        return False
    
    def has_add_permission(self, request):
        """Vérifie les permissions d'ajout."""
        return hasattr(request.user, 'can_manage_users') and request.user.can_manage_users()
    
    def has_view_permission(self, request, obj=None):
        """Vérifie les permissions de lecture."""
        return hasattr(request.user, 'can_manage_users') and request.user.can_manage_users()


# Configuration des titres de l'admin
admin.site.site_header = "Administration EcartsActions"
admin.site.site_title = "EcartsActions Admin"
admin.site.index_title = "Panneau d'administration"