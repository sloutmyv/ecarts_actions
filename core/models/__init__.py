# Import de tous les modèles pour maintenir la compatibilité
from .services import Service
from .users import User

# Export explicite pour les imports directs
__all__ = ['Service', 'User']