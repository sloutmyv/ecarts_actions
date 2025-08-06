from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .signals import set_current_user


class ForcePasswordChangeMiddleware:
    """
    Middleware pour forcer le changement de mot de passe
    pour les utilisateurs qui ont must_change_password=True
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code exécuté pour chaque requête avant la vue
        
        if (request.user.is_authenticated and 
            hasattr(request.user, 'must_change_password') and 
            request.user.must_change_password):
            
            # Pages autorisées même avec must_change_password=True
            allowed_paths = [
                reverse('change_password'),
                reverse('logout'),
                '/admin/logout/',  # Admin logout
            ]
            
            # Permettre les requêtes AJAX et les assets statiques
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            is_htmx = 'HX-Request' in request.headers
            
            if (request.path not in allowed_paths and 
                not request.path.startswith('/static/') and
                not request.path.startswith('/media/') and
                not is_ajax and
                not is_htmx):
                
                messages.warning(request, 'Vous devez changer votre mot de passe avant de continuer.')
                return redirect('change_password')

        response = self.get_response(request)
        
        # Code exécuté pour chaque requête/réponse après la vue
        
        return response


class HistoriqueMiddleware:
    """
    Middleware pour capturer l'utilisateur actuel dans les signaux d'historique.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Définir l'utilisateur actuel pour les signaux
        if request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)

        response = self.get_response(request)
        return response