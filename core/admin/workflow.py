"""
Configuration de l'admin Django pour les modèles workflow.
"""
from django.contrib import admin
from ..models.workflow import ValidateurService


@admin.register(ValidateurService)
class ValidateurServiceAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour ValidateurService."""
    
    list_display = [
        'service', 
        'audit_source', 
        'validateur_name', 
        'niveau', 
        'created_at'
    ]
    list_filter = [
        'niveau', 
        'audit_source',
        'service',
        'created_at'
    ]
    search_fields = [
        'service__nom', 
        'validateur__first_name', 
        'validateur__last_name', 
        'validateur__email'
    ]
    ordering = ['service__nom', 'audit_source__name', 'niveau']
    
    fieldsets = (
        ('Assignation', {
            'fields': ('service', 'audit_source', 'validateur', 'niveau')
        }),
    )
    
    def validateur_name(self, obj):
        """Affiche le nom complet du validateur."""
        return obj.validateur.get_full_name() or obj.validateur.email
    
    validateur_name.short_description = 'Validateur'
    validateur_name.admin_order_field = 'validateur__last_name'