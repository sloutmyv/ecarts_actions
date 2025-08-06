"""
Template tags et filtres pour l'historique des modifications.
"""
import json
from django import template

register = template.Library()


@register.filter
def pprint(value):
    """
    Formatte un objet JSON pour un affichage lisible.
    """
    if value is None:
        return "Non défini"
    
    try:
        if isinstance(value, str):
            # Si c'est déjà une chaîne, essayer de la parser comme JSON
            parsed = json.loads(value)
        else:
            parsed = value
        
        # Reformater avec indentation pour lisibilité
        return json.dumps(parsed, indent=2, ensure_ascii=False, sort_keys=True)
    except (json.JSONDecodeError, TypeError):
        # Si ce n'est pas du JSON valide, retourner tel quel
        return str(value)