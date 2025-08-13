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
        'matricule', 'get_full_name', 'email', 'actif', 'droits_badge', 'service_link', 
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
                # Vérifier les contraintes de validateur
                elif not user.can_be_deactivated():
                    reason = user.get_deactivation_blocking_reason()
                    blocked_users.append(f"{user.get_full_name()}: {reason}")
                else:
                    user.actif = False
                    user.save()
                    updated_count += 1
        
        if updated_count:
            messages.success(request, f'{updated_count} utilisateur(s) désactivé(s) avec succès.')
        
        if blocked_users:
            error_msg = "Impossible de désactiver les utilisateurs suivants:\n"
            for blocked in blocked_users:
                error_msg += f"• {blocked}\n"
            error_msg += "\nActions requises avant désactivation:"
            error_msg += "\n• Pour les rôles de validateur: retirer l'utilisateur du workflow de validation"
            error_msg += "\n• Pour les déclarations d'écarts: transférer vers d'autres utilisateurs actifs"
            messages.error(request, error_msg)
        
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
        
        # Si on modifie un utilisateur existant et qu'on essaie de le désactiver
        if change and 'actif' in form.changed_data:
            # Si on essaie de passer l'utilisateur à inactif
            if not obj.actif:
                # Empêcher la désactivation de son propre compte
                if obj == request.user:
                    messages.error(
                        request,
                        f"Impossible de désactiver votre propre compte '{obj.get_full_name()}'."
                    )
                    # Rétablir le statut actif
                    obj.actif = True
                elif not obj.can_be_deactivated():
                    reason = obj.get_deactivation_blocking_reason()
                    messages.error(
                        request,
                        f"{reason}\n\n"
                        f"Actions requises avant désactivation:\n"
                        f"• Retirer l'utilisateur du workflow de validation\n"
                        f"• Ou transférer ses rôles vers d'autres utilisateurs"
                    )
                    # Rétablir le statut actif
                    obj.actif = True
        
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """
        Validation personnalisée avant suppression.
        Empêche la suppression d'un utilisateur avec des déclarations d'écarts.
        """
        # Empêcher la suppression de son propre compte
        if obj == request.user:
            messages.error(
                request,
                f"Impossible de supprimer votre propre compte '{obj.get_full_name()}'."
            )
            return  # Annuler la suppression
        
        # Vérifier les déclarations d'écarts associées
        if not obj.can_be_deleted():
            reason = obj.get_deletion_blocking_reason()
            messages.error(
                request,
                f"{reason}\n\n"
                f"Vous devez d'abord transférer les déclarations d'écarts vers un autre utilisateur actif "
                f"avant de pouvoir supprimer cet utilisateur."
            )
            return  # Annuler la suppression
        
        # Si toutes les vérifications passent, procéder à la suppression
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """
        Validation personnalisée pour suppression en lot.
        Empêche la suppression des utilisateurs avec des contraintes.
        """
        blocked_users = []
        deletable_users = []
        
        for user in queryset:
            # Empêcher la suppression de son propre compte
            if user == request.user:
                blocked_users.append(f"{user.get_full_name()}: votre propre compte")
                continue
            
            # Vérifier les contraintes (déclarations d'écarts et rôles de validateur)
            if not user.can_be_deleted():
                reason = user.get_deletion_blocking_reason()
                blocked_users.append(f"{user.get_full_name()}: {reason}")
            else:
                deletable_users.append(user)
        
        # Supprimer seulement les utilisateurs sans contraintes
        if deletable_users:
            deleted_count = len(deletable_users)
            for user in deletable_users:
                user.delete()
            messages.success(request, f'{deleted_count} utilisateur(s) supprimé(s) avec succès.')
        
        # Afficher les utilisateurs bloqués
        if blocked_users:
            error_msg = "Impossible de supprimer les utilisateurs suivants:\n"
            for blocked in blocked_users:
                error_msg += f"• {blocked}\n"
            error_msg += "\nActions requises avant suppression:"
            error_msg += "\n• Pour les rôles de validateur: retirer l'utilisateur du workflow de validation"
            error_msg += "\n• Pour les déclarations d'écarts: transférer vers d'autres utilisateurs actifs"
            messages.error(request, error_msg)
    
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