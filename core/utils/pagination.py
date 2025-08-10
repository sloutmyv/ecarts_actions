"""
Utilitaires de pagination optimisés pour l'application EcartsActions.
Améliore les performances avec de nombreux utilisateurs concurrents.
"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404


class OptimizedPaginator(Paginator):
    """
    Paginator optimisé qui utilise count() efficacement.
    """
    def __init__(self, object_list, per_page, **kwargs):
        # Configuration adaptée pour les gros volumes
        self.per_page = min(per_page, 100)  # Maximum 100 éléments par page
        super().__init__(object_list, self.per_page, **kwargs)


def paginate_queryset(request, queryset, per_page=25):
    """
    Pagine un QuerySet de manière optimisée.
    
    Args:
        request: Requête HTTP
        queryset: QuerySet à paginer
        per_page: Nombre d'éléments par page (défaut: 25)
    
    Returns:
        tuple: (page_obj, is_paginated)
    """
    # Limiter le nombre d'éléments par page pour éviter les surcharges
    per_page = min(per_page, 100)
    
    paginator = OptimizedPaginator(queryset, per_page)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        # Si la page n'est pas un entier, utiliser la première page
        page_obj = paginator.page(1)
    except EmptyPage:
        # Si la page est hors limites, utiliser la dernière page
        page_obj = paginator.page(paginator.num_pages)
    
    is_paginated = paginator.num_pages > 1
    
    return page_obj, is_paginated


def get_page_range(page_obj, max_pages=10):
    """
    Génère une plage de pages pour l'affichage de la navigation.
    
    Args:
        page_obj: Objet page du paginator
        max_pages: Nombre maximum de pages à afficher
    
    Returns:
        dict: Informations de pagination pour le template
    """
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    
    # Calculer la plage de pages à afficher
    half_range = max_pages // 2
    start_page = max(1, current_page - half_range)
    end_page = min(total_pages, current_page + half_range)
    
    # Ajuster si on est près du début ou de la fin
    if end_page - start_page < max_pages - 1:
        if start_page == 1:
            end_page = min(total_pages, start_page + max_pages - 1)
        else:
            start_page = max(1, end_page - max_pages + 1)
    
    page_range = range(start_page, end_page + 1)
    
    return {
        'page_range': page_range,
        'show_first': start_page > 1,
        'show_last': end_page < total_pages,
        'show_prev_dots': start_page > 2,
        'show_next_dots': end_page < total_pages - 1,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
        'current_page': current_page,
        'total_pages': total_pages,
        'total_items': page_obj.paginator.count
    }


def build_pagination_url(request, page_number):
    """
    Construit une URL de pagination en préservant les paramètres de requête.
    
    Args:
        request: Requête HTTP
        page_number: Numéro de page
    
    Returns:
        str: URL avec les paramètres appropriés
    """
    params = request.GET.copy()
    params['page'] = page_number
    return f"{request.path}?{params.urlencode()}"