"""
Template tags et filtres pour la gestion du workflow.
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Filtre pour récupérer un élément d'un dictionnaire par clé.
    
    Usage: {{ my_dict|get_item:my_key }}
    """
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    elif dictionary and isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def get_validators_by_level(validateurs_queryset, niveau):
    """
    Filtre pour récupérer les validateurs d'un niveau spécifique.
    
    Usage: {{ validateurs|get_validators_by_level:1 }}
    """
    if validateurs_queryset:
        return validateurs_queryset.filter(niveau=niveau)
    return []


@register.simple_tag
def niveau_badge_class(niveau):
    """
    Tag pour retourner la classe CSS du badge selon le niveau.
    
    Usage: {% niveau_badge_class 1 %}
    """
    classes = {
        1: 'bg-green-500',
        2: 'bg-blue-500', 
        3: 'bg-purple-500',
    }
    return classes.get(niveau, 'bg-gray-500')


@register.simple_tag
def niveau_text_class(niveau):
    """
    Tag pour retourner la classe CSS du texte selon le niveau.
    
    Usage: {% niveau_text_class 1 %}
    """
    classes = {
        1: 'text-green-600 hover:text-green-800',
        2: 'text-blue-600 hover:text-blue-800', 
        3: 'text-purple-600 hover:text-purple-800',
    }
    return classes.get(niveau, 'text-gray-600 hover:text-gray-800')


@register.simple_tag
def niveau_bg_class(niveau):
    """
    Tag pour retourner la classe CSS du background selon le niveau.
    
    Usage: {% niveau_bg_class 1 %}
    """
    classes = {
        1: 'bg-green-100 text-green-800',
        2: 'bg-blue-100 text-blue-800', 
        3: 'bg-purple-100 text-purple-800',
    }
    return classes.get(niveau, 'bg-gray-100 text-gray-800')


@register.filter
def is_validator_for_gap(user, gap):
    """
    Détermine si un utilisateur peut valider un écart donné.
    
    Usage: {{ user|is_validator_for_gap:gap }}
    """
    # Administrateurs peuvent toujours valider
    if user.droits in ['SA', 'AD']:
        return True
    
    # Vérifier si l'utilisateur est validateur pour ce service/source d'audit
    try:
        from core.models.workflow import ValidateurService
        validator_assignments = ValidateurService.get_services_validateur(
            user, actif_seulement=True
        ).filter(
            service=gap.gap_report.service,
            audit_source=gap.gap_report.audit_source
        )
        return validator_assignments.exists()
    except Exception:
        return False