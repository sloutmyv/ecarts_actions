"""
Backend d'authentification personnalisé pour utiliser le matricule au lieu du username.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class MatriculeAuthBackend(ModelBackend):
    """
    Backend d'authentification qui utilise le matricule au lieu du username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un utilisateur en utilisant son matricule.
        """
        if username is None or password is None:
            return None
        
        try:
            # Chercher l'utilisateur par matricule (insensible à la casse)
            user = User.objects.get(matricule=username.upper())
        except User.DoesNotExist:
            # Exécuter le hashage du mot de passe pour éviter les attaques de timing
            User().set_password(password)
            return None
        
        # Vérifier le mot de passe et que l'utilisateur est actif
        if user.check_password(password) and self.user_can_authenticate(user) and user.actif:
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID.
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) and user.actif else None