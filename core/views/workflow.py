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
from ..models import ValidateurService, Service, User, AuditSource


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
    
    # Récupérer tous les utilisateurs actifs et toutes les sources d'audit
    validateurs = User.objects.all().order_by('nom', 'prenom')
    audit_sources = AuditSource.objects.all().order_by('name')
    
    # Créer une structure Service × Source d'audit avec leurs validateurs
    services_avec_validateurs = []
    services_sans_validateurs = []
    
    for service in services_feuilles:
        service_has_validators = False
        audit_sources_data = []
        sources_sans_validateurs_count = 0
        
        for audit_source in audit_sources:
            niveau_1 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=1)
            niveau_2 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=2)
            niveau_3 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=3)
            
            # Vérifier si cette combinaison service/source a au moins un validateur
            has_validators_for_source = niveau_1.exists() or niveau_2.exists() or niveau_3.exists()
            if has_validators_for_source:
                service_has_validators = True
            else:
                sources_sans_validateurs_count += 1
            
            audit_source_data = {
                'audit_source': audit_source,
                'niveau_1': niveau_1,
                'niveau_2': niveau_2,
                'niveau_3': niveau_3,
                'has_validators': has_validators_for_source,
            }
            audit_sources_data.append(audit_source_data)
        
        service_data = {
            'service': service,
            'audit_sources': audit_sources_data,
            'has_validators': service_has_validators,
            'sources_sans_validateurs_count': sources_sans_validateurs_count,
            'total_sources_count': len(audit_sources),
        }
        services_avec_validateurs.append(service_data)
        
        if not service_has_validators:
            services_sans_validateurs.append(service)
    
    context = {
        'page_title': 'Gestion du Workflow',
        'services_feuilles': services_feuilles,
        'validateurs': validateurs,
        'audit_sources': audit_sources,
        'services_avec_validateurs': services_avec_validateurs,
        'services_sans_validateurs': services_sans_validateurs,
        'services_sans_validateurs_count': len(services_sans_validateurs),
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
        audit_source_id = request.POST.get('audit_source_id')
        validateur_id = request.POST.get('validateur_id')
        niveau = int(request.POST.get('niveau'))
        
        if not all([service_id, audit_source_id, validateur_id, niveau]):
            return JsonResponse({
                'success': False,
                'error': 'Paramètres manquants'
            }, status=400)
        
        service = get_object_or_404(Service, pk=service_id)
        audit_source = get_object_or_404(AuditSource, pk=audit_source_id)
        validateur = get_object_or_404(User, pk=validateur_id)
        
        with transaction.atomic():
            # Vérifier s'il existe déjà un validateur actif pour ce niveau/service/source
            existing_validator = ValidateurService.objects.filter(
                service=service,
                audit_source=audit_source,
                niveau=niveau,
                actif=True
            ).first()
            
            if existing_validator:
                # Si c'est le même validateur, ne rien faire
                if existing_validator.validateur == validateur:
                    return JsonResponse({
                        'success': True,
                        'message': f'{validateur.get_full_name()} est déjà assigné au service {service.nom} '
                                 f'pour {audit_source.name} (Niveau {niveau})'
                    })
                else:
                    # Remplacer le validateur existant
                    existing_validator.validateur = validateur
                    existing_validator.save()
                    validateur_service = existing_validator
                    created = False
            else:
                # Créer une nouvelle assignation ou réactiver une existante
                validateur_service, created = ValidateurService.objects.get_or_create(
                    service=service,
                    audit_source=audit_source,
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
            'message': f'{validateur.get_full_name()} assigné au service {service.nom} '
                      f'pour {audit_source.name} (Niveau {niveau})'
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
def remove_validator(request, validateur_service_id):
    """
    Gère la suppression d'un validateur (GET: confirmation, POST: suppression effective).
    """
    validateur_service = get_object_or_404(ValidateurService, pk=validateur_service_id)
    
    if request.method == 'GET':
        # Vérifier s'il s'agit du dernier validateur du service pour cette source d'audit
        validators_count = ValidateurService.objects.filter(
            service=validateur_service.service,
            audit_source=validateur_service.audit_source,
            actif=True
        ).count()
        
        is_last_validator = validators_count <= 1
        
        # Retourner le modal de confirmation
        context = {
            'validateur_service': validateur_service,
            'is_last_validator': is_last_validator,
            'message': f'Êtes-vous sûr de vouloir retirer {validateur_service.validateur.get_full_name()} '
                      f'du niveau {validateur_service.niveau} du service {validateur_service.service.nom} '
                      f'pour la source d\'audit {validateur_service.audit_source.name} ?'
        }
        return render(request, 'core/workflow/validator_delete_confirm.html', context)
    
    elif request.method == 'POST':
        # Effectuer la suppression
        try:
            # Vérifier s'il s'agit du dernier validateur pour cette source d'audit
            validators_count = ValidateurService.objects.filter(
                service=validateur_service.service,
                audit_source=validateur_service.audit_source,
                actif=True
            ).count()
            
            if validators_count <= 1:
                return JsonResponse({
                    'success': False,
                    'error': 'Impossible de supprimer le dernier validateur d\'une combinaison service/source d\'audit. '
                            'Chaque combinaison doit avoir au moins un validateur.'
                }, status=400)
            
            service_nom = validateur_service.service.nom
            validateur_nom = validateur_service.validateur.get_full_name()
            niveau = validateur_service.niveau
            
            # Supprimer l'assignation
            validateur_service.delete()
            
            messages.success(request, f"Validateur retiré du service {service_nom}")
            
            # Retourner une réponse HTMX qui ferme le modal et recharge la page
            from django.http import HttpResponse
            return HttpResponse(
                '<script>document.getElementById("modal-container").innerHTML = ""; window.location.reload();</script>'
            )
            
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
def service_detail_api(request, service_id):
    """
    API endpoint pour récupérer les détails d'un service avec ses validateurs par source d'audit.
    """
    try:
        service = get_object_or_404(Service, pk=service_id)
        audit_sources = AuditSource.objects.all().order_by('name')
        
        service_data = {
            'id': service.id,
            'nom': service.nom,
            'code': service.code,
            'audit_sources': []
        }
        
        for audit_source in audit_sources:
            niveau_1 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=1)
            niveau_2 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=2)
            niveau_3 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=3)
            
            audit_source_data = {
                'audit_source': {
                    'id': audit_source.id,
                    'name': audit_source.name,
                    'description': audit_source.description
                },
                'niveau_1': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_1
                ],
                'niveau_2': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_2
                ],
                'niveau_3': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_3
                ]
            }
            
            service_data['audit_sources'].append(audit_source_data)
        
        return JsonResponse({
            'success': True,
            'service': service_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def search_users(request):
    """
    API endpoint pour la recherche d'utilisateurs.
    Utilisé pour l'autocomplétion dans l'assignation de validateurs.
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'users': []
            })
        
        # Recherche par matricule ou nom/prénom
        users = User.objects.filter(
            models.Q(matricule__icontains=query) |
            models.Q(nom__icontains=query) |
            models.Q(prenom__icontains=query)
        ).order_by('nom', 'prenom')[:10]  # Limiter à 10 résultats
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'matricule': user.matricule,
                'nom_complet': user.get_full_name(),
                'service': user.get_service_path(),
                'droits': user.get_droits_display()
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def service_detail_api(request, service_id):
    """
    API endpoint pour récupérer les détails d'un service avec ses validateurs par source d'audit.
    """
    try:
        service = get_object_or_404(Service, pk=service_id)
        audit_sources = AuditSource.objects.all().order_by('name')
        
        service_data = {
            'id': service.id,
            'nom': service.nom,
            'code': service.code,
            'audit_sources': []
        }
        
        for audit_source in audit_sources:
            niveau_1 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=1)
            niveau_2 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=2)
            niveau_3 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=3)
            
            audit_source_data = {
                'audit_source': {
                    'id': audit_source.id,
                    'name': audit_source.name,
                    'description': audit_source.description
                },
                'niveau_1': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_1
                ],
                'niveau_2': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_2
                ],
                'niveau_3': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_3
                ]
            }
            
            service_data['audit_sources'].append(audit_source_data)
        
        return JsonResponse({
            'success': True,
            'service': service_data
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


@staff_member_required
def service_detail_api(request, service_id):
    """
    API endpoint pour récupérer les détails d'un service avec ses validateurs par source d'audit.
    """
    try:
        service = get_object_or_404(Service, pk=service_id)
        audit_sources = AuditSource.objects.all().order_by('name')
        
        service_data = {
            'id': service.id,
            'nom': service.nom,
            'code': service.code,
            'audit_sources': []
        }
        
        for audit_source in audit_sources:
            niveau_1 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=1)
            niveau_2 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=2)
            niveau_3 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=3)
            
            audit_source_data = {
                'audit_source': {
                    'id': audit_source.id,
                    'name': audit_source.name,
                    'description': audit_source.description
                },
                'niveau_1': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_1
                ],
                'niveau_2': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_2
                ],
                'niveau_3': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_3
                ]
            }
            
            service_data['audit_sources'].append(audit_source_data)
        
        return JsonResponse({
            'success': True,
            'service': service_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def search_users(request):
    """
    API endpoint pour la recherche d'utilisateurs.
    Utilisé pour l'autocomplétion dans l'assignation de validateurs.
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'users': []
            })
        
        # Recherche par matricule ou nom/prénom
        users = User.objects.filter(
            models.Q(matricule__icontains=query) |
            models.Q(nom__icontains=query) |
            models.Q(prenom__icontains=query)
        ).order_by('nom', 'prenom')[:10]  # Limiter à 10 résultats
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'matricule': user.matricule,
                'nom_complet': user.get_full_name(),
                'service': user.get_service_path(),
                'droits': user.get_droits_display()
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@staff_member_required
def service_detail_api(request, service_id):
    """
    API endpoint pour récupérer les détails d'un service avec ses validateurs par source d'audit.
    """
    try:
        service = get_object_or_404(Service, pk=service_id)
        audit_sources = AuditSource.objects.all().order_by('name')
        
        service_data = {
            'id': service.id,
            'nom': service.nom,
            'code': service.code,
            'audit_sources': []
        }
        
        for audit_source in audit_sources:
            niveau_1 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=1)
            niveau_2 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=2)
            niveau_3 = ValidateurService.get_validateurs_service(service, audit_source=audit_source, niveau=3)
            
            audit_source_data = {
                'audit_source': {
                    'id': audit_source.id,
                    'name': audit_source.name,
                    'description': audit_source.description
                },
                'niveau_1': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_1
                ],
                'niveau_2': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_2
                ],
                'niveau_3': [
                    {
                        'id': vs.id,
                        'validateur': {
                            'id': vs.validateur.id,
                            'prenom': vs.validateur.prenom,
                            'nom': vs.validateur.nom,
                            'matricule': vs.validateur.matricule,
                            'get_full_name': vs.validateur.get_full_name()
                        }
                    } for vs in niveau_3
                ]
            }
            
            service_data['audit_sources'].append(audit_source_data)
        
        return JsonResponse({
            'success': True,
            'service': service_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)