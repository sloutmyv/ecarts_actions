# Import de toutes les configurations admin pour maintenir la compatibilité
from .services import ServiceAdmin
from .users import UserAdmin

# Export explicite pour les imports directs
__all__ = ['ServiceAdmin', 'UserAdmin']