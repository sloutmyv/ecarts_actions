from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from .signals import set_current_user
import time
import logging


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


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware pour surveiller les performances de l'application en production.
    Enregistre les requêtes lentes et surveille l'usage de la base de données.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('ecarts_actions.performance')
        
    def process_request(self, request):
        """Marque le début de la requête."""
        request.start_time = time.time()
        request.queries_start = len(connection.queries)
        
    def process_response(self, request, response):
        """Analyse les performances à la fin de la requête."""
        if not hasattr(request, 'start_time'):
            return response
            
        # Calculer le temps d'exécution
        execution_time = time.time() - request.start_time
        
        # Compter les requêtes DB
        db_queries = len(connection.queries) - getattr(request, 'queries_start', 0)
        
        # Seuil de surveillance configurable
        slow_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0)
        
        # Enregistrer les requêtes lentes
        if execution_time > slow_threshold:
            self.logger.warning(
                f"Requête lente détectée: {request.method} {request.path} - "
                f"Temps: {execution_time:.3f}s - Requêtes DB: {db_queries} - "
                f"User: {getattr(request.user, 'matricule', 'Anonymous')} - "
                f"Status: {response.status_code}"
            )
        
        # Surveiller l'usage excessif de la DB
        if db_queries > 20:  # Seuil configurable
            self.logger.warning(
                f"Trop de requêtes DB: {request.method} {request.path} - "
                f"Requêtes DB: {db_queries} - Temps: {execution_time:.3f}s - "
                f"User: {getattr(request.user, 'matricule', 'Anonymous')}"
            )
        
        # Ajouter des headers de debug pour les administrateurs
        if hasattr(request.user, 'droits') and request.user.droits in ['SA', 'AD']:
            response['X-Execution-Time'] = f"{execution_time:.3f}s"
            response['X-DB-Queries'] = str(db_queries)
        
        return response