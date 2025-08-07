"""
Vues pour la gestion du workflow de validation des écarts.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction, models
from django.core.exceptions import ValidationError
from ..models import ValidateurService, Service, User


@staff_member_required
def workflow_management(request):
    """
    Page principale de gestion du workflow.
    Affiche la matrice des valideurs par service et niveau.
    """
    # Gérer le tri
    sort_by = request.GET.get('sort', 'nom')  # Tri par défaut par nom
    sort_order = request.GET.get('order', 'asc')  # Ordre par défaut croissant
    
    # Construire le champ de tri avec l'ordre
    if sort_order == 'desc':
        order_field = f'-{sort_by}'
    else:
        order_field = sort_by
    
    # Récupérer tous les services feuilles (sans sous-services) avec tri
    valid_sort_fields = ['nom', 'code']
    if sort_by not in valid_sort_fields:
        sort_by = 'nom'
        order_field = sort_by if sort_order == 'asc' else f'-{sort_by}'
    
    services_feuilles = Service.objects.filter(sous_services__isnull=True).order_by(order_field)
    
    # Récupérer tous les validateurs actifs
    validateurs = User.objects.filter(
        droits__in=[User.ADMIN, User.SUPER_ADMIN]
    ).order_by('nom', 'prenom')
    
    # Créer une liste de services avec leurs validateurs
    services_avec_validateurs = []
    for service in services_feuilles:
        service_data = {
            'service': service,
            'niveau_1': ValidateurService.get_validateurs_service(service, niveau=1),
            'niveau_2': ValidateurService.get_validateurs_service(service, niveau=2),
            'niveau_3': ValidateurService.get_validateurs_service(service, niveau=3),
        }
        services_avec_validateurs.append(service_data)
    
    context = {
        'page_title': 'Gestion du Workflow',
        'services_feuilles': services_feuilles,
        'validateurs': validateurs,
        'services_avec_validateurs': services_avec_validateurs,
        'niveaux': ValidateurService.NIVEAU_CHOICES,
        'current_sort': sort_by,
        'current_order': sort_order,
    }
    return render(request, 'core/workflow/management.html', context)


@staff_member_required
@require_POST
def assign_validator(request):
    """
    Assigne un validateur à un service pour un niveau donné.
    Utilisé en AJAX/HTMX.
    """
    try:
        service_id = request.POST.get('service_id')
        validateur_id = request.POST.get('validateur_id')
        niveau = int(request.POST.get('niveau'))
        
        if not all([service_id, validateur_id, niveau]):
            return JsonResponse({
                'success': False,
                'error': 'Paramètres manquants'
            }, status=400)
        
        service = get_object_or_404(Service, pk=service_id)
        validateur = get_object_or_404(User, pk=validateur_id)
        
        with transaction.atomic():
            validateur_service, created = ValidateurService.objects.get_or_create(
                service=service,
                validateur=validateur,
                niveau=niveau,
                defaults={'actif': True}
            )
            
            if not created:
                # Si l'affectation existe déjà, la réactiver
                validateur_service.actif = True
                validateur_service.save()
        
        messages.success(request, f"Validateur assigné avec succès au niveau {niveau}")
        
        return JsonResponse({
            'success': True,
            'message': f'{validateur.get_full_name()} assigné au service {service.nom} (Niveau {niveau})'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'assignation: {str(e)}'
        }, status=500)


@staff_member_required
@require_POST
def remove_validator(request):
    """
    Supprime l'assignation d'un validateur à un service.
    Utilisé en AJAX/HTMX.
    """
    try:
        validateur_service_id = request.POST.get('validateur_service_id')
        
        if not validateur_service_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de l\'assignation manquant'
            }, status=400)
        
        validateur_service = get_object_or_404(ValidateurService, pk=validateur_service_id)
        
        # Garder l'info pour le message
        service_nom = validateur_service.service.nom
        validateur_nom = validateur_service.validateur.get_full_name()
        niveau = validateur_service.niveau
        
        # Supprimer l'assignation
        validateur_service.delete()
        
        messages.success(request, f"Validateur retiré du service {service_nom}")
        
        return JsonResponse({
            'success': True,
            'message': f'{validateur_nom} retiré du service {service_nom} (Niveau {niveau})'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la suppression: {str(e)}'
        }, status=500)


@staff_member_required
@require_POST
def toggle_validator_status(request):
    """
    Active/désactive un validateur pour un service.
    Utilisé en AJAX/HTMX.
    """
    try:
        validateur_service_id = request.POST.get('validateur_service_id')
        
        if not validateur_service_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de l\'assignation manquant'
            }, status=400)
        
        validateur_service = get_object_or_404(ValidateurService, pk=validateur_service_id)
        
        # Inverser le statut actif
        validateur_service.actif = not validateur_service.actif
        validateur_service.save()
        
        status_text = "activé" if validateur_service.actif else "désactivé"
        messages.success(request, f"Validateur {status_text}")
        
        return JsonResponse({
            'success': True,
            'actif': validateur_service.actif,
            'message': f'Validateur {status_text}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du changement de statut: {str(e)}'
        }, status=500)


@staff_member_required
def get_service_validators(request, service_id):
    """
    Retourne la liste des validateurs d'un service en JSON.
    Utilisé pour les appels AJAX.
    """
    try:
        service = get_object_or_404(Service, pk=service_id)
        validateurs = ValidateurService.objects.filter(
            service=service,
            actif=True
        ).select_related('validateur').order_by('niveau')
        
        data = []
        for vs in validateurs:
            data.append({
                'id': vs.id,
                'validateur_id': vs.validateur.id,
                'validateur_nom': vs.validateur.get_full_name(),
                'validateur_matricule': vs.validateur.matricule,
                'niveau': vs.niveau,
                'niveau_display': vs.get_niveau_display(),
                'actif': vs.actif,
            })
        
        return JsonResponse({
            'success': True,
            'service': {
                'id': service.id,
                'nom': service.nom,
                'code': service.code,
            },
            'validateurs': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def workflow_stats(request):
    """
    Retourne des statistiques sur la configuration du workflow.
    """
    try:
        stats = {
            'total_services': Service.objects.filter(sous_services__isnull=True).count(),
            'services_avec_valideurs': ValidateurService.objects.values('service').distinct().count(),
            'total_assignations': ValidateurService.objects.filter(actif=True).count(),
            'assignations_par_niveau': {
                'niveau_1': ValidateurService.objects.filter(actif=True, niveau=1).count(),
                'niveau_2': ValidateurService.objects.filter(actif=True, niveau=2).count(),
                'niveau_3': ValidateurService.objects.filter(actif=True, niveau=3).count(),
            }
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)