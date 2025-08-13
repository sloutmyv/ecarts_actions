"""
Utilitaires de cache pour l'application EcartsActions.
Optimise les performances pour un usage avec de nombreux utilisateurs concurrents.
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def cache_key_for_user(base_key, user, **kwargs):
    """
    Génère une clé de cache unique basée sur l'utilisateur et des paramètres.
    
    Args:
        base_key: Clé de base
        user: Instance utilisateur
        **kwargs: Paramètres additionnels pour la clé
    """
    key_data = {
        'user_id': user.id if user and user.is_authenticated else 'anonymous',
        'user_droits': getattr(user, 'droits', None) if user and user.is_authenticated else None,
        'user_service_id': user.service_id if user and user.is_authenticated and hasattr(user, 'service') else None,
        **kwargs
    }
    
    # Créer un hash des données pour une clé courte et unique
    key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:8]
    
    return f"{base_key}:{key_hash}"


def cache_user_dependent(timeout=300, cache_alias='default'):
    """
    Décorateur pour mettre en cache les résultats des vues en fonction de l'utilisateur.
    
    Args:
        timeout: Durée de cache en secondes (défaut: 5 minutes)
        cache_alias: Alias du cache à utiliser
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Générer une clé unique basée sur la vue, les arguments et l'utilisateur
            cache_key = cache_key_for_user(
                f"view:{view_func.__name__}",
                request.user,
                args=args,
                kwargs=kwargs,
                query_params=dict(request.GET.items())
            )
            
            # Essayer de récupérer depuis le cache
            cached_result = cache.get(cache_key, alias=cache_alias)
            if cached_result is not None:
                return cached_result
            
            # Exécuter la vue et mettre en cache le résultat
            result = view_func(request, *args, **kwargs)
            cache.set(cache_key, result, timeout, alias=cache_alias)
            
            return result
        return wrapper
    return decorator


def cache_queryset(timeout=300, cache_alias='default'):
    """
    Décorateur pour mettre en cache les résultats de QuerySet.
    
    Args:
        timeout: Durée de cache en secondes
        cache_alias: Alias du cache à utiliser
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer une clé de cache basée sur la fonction et ses arguments
            cache_key_data = {
                'func': func.__name__,
                'args': [str(arg) for arg in args],
                'kwargs': {k: str(v) for k, v in kwargs.items()}
            }
            cache_key_hash = hashlib.md5(
                json.dumps(cache_key_data, sort_keys=True).encode()
            ).hexdigest()[:8]
            cache_key = f"queryset:{func.__name__}:{cache_key_hash}"
            
            # Essayer de récupérer depuis le cache
            cached_result = cache.get(cache_key, alias=cache_alias)
            if cached_result is not None:
                return cached_result
            
            # Exécuter la fonction et mettre en cache le résultat
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout, alias=cache_alias)
            
            return result
        return wrapper
    return decorator


def invalidate_user_cache(user, pattern=None):
    """
    Invalide le cache pour un utilisateur spécifique.
    
    Args:
        user: Instance utilisateur
        pattern: Pattern optionnel pour limiter l'invalidation
    """
    # Note: Django-Redis supporte la suppression par pattern
    if hasattr(cache, 'delete_pattern'):
        if pattern:
            cache.delete_pattern(f"*user:{user.id}*{pattern}*")
        else:
            cache.delete_pattern(f"*user:{user.id}*")


def get_cached_services():
    """
    Récupère la liste hiérarchique des services depuis le cache.
    Cache pendant 1 heure car ces données changent rarement.
    """
    cache_key = "services:hierarchical_list"
    services = cache.get(cache_key)
    
    if services is None:
        from core.views.gaps import get_services_hierarchical_order
        services = get_services_hierarchical_order()
        cache.set(cache_key, services, 3600)  # 1 heure
    
    return services


def get_cached_gap_types():
    """
    Récupère la liste des types d'écarts depuis le cache.
    Cache pendant 30 minutes.
    """
    cache_key = "gap_types:all"
    gap_types = cache.get(cache_key)
    
    if gap_types is None:
        from core.models import GapType
        gap_types = list(GapType.objects.filter(is_active=True).order_by('audit_source__name', 'name'))
        cache.set(cache_key, gap_types, 1800)  # 30 minutes
    
    return gap_types


def get_cached_audit_sources():
    """
    Récupère la liste des sources d'audit depuis le cache.
    Cache pendant 1 heure car ces données changent rarement.
    """
    cache_key = "audit_sources:all"
    audit_sources = cache.get(cache_key)
    
    if audit_sources is None:
        from core.models import AuditSource
        audit_sources = list(AuditSource.objects.filter(is_active=True).order_by('name'))
        cache.set(cache_key, audit_sources, 3600)  # 1 heure
    
    return audit_sources


def invalidate_reference_data_cache():
    """
    Invalide le cache des données de référence (services, types d'écarts, sources d'audit).
    À appeler quand ces données sont modifiées via l'admin.
    """
    # Vider les caches principaux
    cache.delete_many([
        "services:hierarchical_list",
        "gap_types:all", 
        "audit_sources:all"
    ])
    
    # Vider aussi tous les caches par audit_source
    # Note: En l'absence d'une méthode pour lister toutes les clés, on vide tout le cache
    # pour s'assurer que les caches gap_types:audit_source:* sont supprimés
    cache.clear()