"""
Vues optimisées pour la gestion du workflow de validation des écarts.
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from ..models import ValidateurService, Service, User, AuditSource


@staff_member_required
def workflow_management(request):
    """
    Page principale de gestion du workflow optimisée.
    Affiche la matrice des valideurs par service et niveau avec requêtes optimisées.
    """
    # Gérer le tri
    sort_by = request.GET.get('sort', 'nom')
    sort_order = request.GET.get('order', 'asc')
    
    # Construire le champ de tri avec l'ordre
    if sort_order == 'desc':
        order_field = f'-{sort_by}'
    else:
        order_field = sort_by
    
    # Validation du champ de tri
    valid_sort_fields = ['nom', 'code']
    if sort_by not in valid_sort_fields:
        sort_by = 'nom'
        order_field = sort_by if sort_order == 'asc' else f'-{sort_by}'
    
    # Récupérer les services avec optimisation des requêtes
    services_feuilles = Service.objects.filter(
        sous_services__isnull=True
    ).prefetch_related(
        Prefetch(
            'validateurs',
            queryset=ValidateurService.objects.filter(actif=True).select_related(
                'validateur', 'audit_source'
            )
        )
    ).order_by(order_field)
    
    # Récupérer tous les utilisateurs actifs et toutes les sources d'audit
    validateurs = User.objects.all().order_by('nom', 'prenom')
    audit_sources = AuditSource.objects.all().order_by('name')
    
    # Créer une structure optimisée Service × Source d'audit avec leurs validateurs
    services_avec_validateurs = []
    services_sans_validateurs = []
    
    # Pré-créer un dictionnaire des validateurs par service/source/niveau pour éviter les requêtes N+1
    validateurs_dict = {}
    for service in services_feuilles:
        validateurs_dict[service.id] = {}
        for audit_source in audit_sources:
            validateurs_dict[service.id][audit_source.id] = {1: None, 2: None, 3: None}
    
    # Remplir le dictionnaire avec les validateurs existants
    for vs in ValidateurService.objects.filter(
        service__in=services_feuilles, 
        actif=True
    ).select_related('validateur', 'service', 'audit_source'):
        if vs.service.id in validateurs_dict and vs.audit_source.id in validateurs_dict[vs.service.id]:
            validateurs_dict[vs.service.id][vs.audit_source.id][vs.niveau] = vs
    
    for service in services_feuilles:
        service_has_validators = False
        audit_sources_data = []
        sources_sans_validateurs_count = 0
        
        for audit_source in audit_sources:
            niveau_1 = validateurs_dict[service.id][audit_source.id][1]
            niveau_2 = validateurs_dict[service.id][audit_source.id][2]
            niveau_3 = validateurs_dict[service.id][audit_source.id][3]
            
            # Vérifier si cette combinaison service/source a au moins un validateur
            has_validators_for_source = any([niveau_1, niveau_2, niveau_3])
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
        
        # Calculer le nombre de sources configurées
        sources_configurees_count = len(audit_sources) - sources_sans_validateurs_count
        
        service_data = {
            'service': service,
            'audit_sources': audit_sources_data,
            'has_validators': service_has_validators,
            'sources_sans_validateurs_count': sources_sans_validateurs_count,
            'sources_configurees_count': sources_configurees_count,
            'total_sources_count': len(audit_sources),
        }
        services_avec_validateurs.append(service_data)
        
        if not service_has_validators:
            services_sans_validateurs.append(service)
    
    # Calculer les statistiques globales
    services_completement_configures = sum(1 for data in services_avec_validateurs if data['sources_sans_validateurs_count'] == 0)
    
    context = {
        'page_title': 'Gestion du Workflow',
        'services_feuilles': services_feuilles,
        'validateurs': validateurs,
        'audit_sources': audit_sources,
        'services_avec_validateurs': services_avec_validateurs,
        'services_sans_validateurs': services_sans_validateurs,
        'services_sans_validateurs_count': len(services_sans_validateurs),
        'services_completement_configures': services_completement_configures,
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
    Version optimisée avec HTMX pur.
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
                        'message': f'{validateur.get_full_name()} est déjà assigné'
                    })
                else:
                    # Remplacer le validateur existant
                    existing_validator.validateur = validateur
                    existing_validator.save()
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
                    validateur_service.actif = True
                    validateur_service.save()
        
        # Retourner le fragment HTML mis à jour pour la section détaillée
        niveau_partial_context = {
            'service': service,
            'audit_source': audit_source,
            'niveau': niveau,
            'validateur_assigne': ValidateurService.objects.filter(
                service=service, audit_source=audit_source, niveau=niveau, actif=True
            ).first()
        }
        
        from django.template.loader import render_to_string
        niveau_partial_html = render_to_string('core/workflow/niveau_partial.html', niveau_partial_context, request)
        
        # Récupérer les données mises à jour pour l'aperçu des badges
        audit_sources_data = []
        for audit_source_obj in AuditSource.objects.all():
            validateurs_niveaux = ValidateurService.objects.filter(
                service=service, audit_source=audit_source_obj, actif=True
            )
            
            niveau_1 = validateurs_niveaux.filter(niveau=1).first()
            niveau_2 = validateurs_niveaux.filter(niveau=2).first()
            niveau_3 = validateurs_niveaux.filter(niveau=3).first()
            
            has_validators = niveau_1 or niveau_2 or niveau_3
            
            if has_validators:
                audit_sources_data.append({
                    'audit_source': audit_source_obj,
                    'niveau_1': niveau_1,
                    'niveau_2': niveau_2,
                    'niveau_3': niveau_3,
                    'has_validators': has_validators
                })
        
        # Retourner les deux fragments HTML
        overview_context = {
            'audit_sources_data': audit_sources_data
        }
        overview_html = render_to_string('core/workflow/service_overview_badges.html', overview_context, request)
        
        return JsonResponse({
            'success': True,
            'niveau_html': niveau_partial_html,
            'overview_html': overview_html,
            'service_id': service.id,
            'audit_source_id': audit_source.id,
            'niveau': niveau
        })
        
    except Exception as e:
        return HttpResponse(
            f'<div class="text-red-500 text-sm">Erreur: {str(e)}</div>', 
            status=500
        )


@staff_member_required
def remove_validator(request, validateur_service_id):
    """
    Gère la suppression d'un validateur avec confirmation optimisée.
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
        try:
            service = validateur_service.service
            audit_source = validateur_service.audit_source
            niveau = validateur_service.niveau
            
            # Supprimer l'assignation
            validateur_service.delete()
            
            # Retourner le fragment HTML mis à jour pour la section détaillée
            from django.template.loader import render_to_string
            niveau_partial_context = {
                'service': service,
                'audit_source': audit_source,
                'niveau': niveau,
                'validateur_assigne': None
            }
            niveau_partial_html = render_to_string('core/workflow/niveau_partial.html', niveau_partial_context, request)
            
            # Récupérer les données mises à jour pour l'aperçu des badges
            audit_sources_data = []
            for audit_source_obj in AuditSource.objects.all():
                validateurs_niveaux = ValidateurService.objects.filter(
                    service=service, audit_source=audit_source_obj, actif=True
                )
                
                niveau_1 = validateurs_niveaux.filter(niveau=1).first()
                niveau_2 = validateurs_niveaux.filter(niveau=2).first()
                niveau_3 = validateurs_niveaux.filter(niveau=3).first()
                
                has_validators = niveau_1 or niveau_2 or niveau_3
                
                if has_validators:
                    audit_sources_data.append({
                        'audit_source': audit_source_obj,
                        'niveau_1': niveau_1,
                        'niveau_2': niveau_2,
                        'niveau_3': niveau_3,
                        'has_validators': has_validators
                    })
            
            # Générer l'HTML pour l'aperçu
            overview_context = {
                'audit_sources_data': audit_sources_data
            }
            overview_html = render_to_string('core/workflow/service_overview_badges.html', overview_context, request)
            
            # Si la requête vient d'HTMX, on retourne JSON
            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'success': True,
                    'niveau_html': niveau_partial_html,
                    'overview_html': overview_html,
                    'service_id': service.id,
                    'close_modal': True
                })
            else:
                # Compatibilité avec les anciennes requêtes
                return HttpResponse(niveau_partial_html)
            
        except Exception as e:
            return HttpResponse(
                f'<div class="text-red-500 text-sm">Erreur: {str(e)}</div>', 
                status=500
            )


@staff_member_required
def search_users(request):
    """
    API endpoint optimisée pour la recherche d'utilisateurs.
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'users': []
            })
        
        # Recherche optimisée avec select_related
        users = User.objects.filter(
            models.Q(matricule__icontains=query) |
            models.Q(nom__icontains=query) |
            models.Q(prenom__icontains=query)
        ).select_related('service').order_by('nom', 'prenom')[:10]
        
        users_data = [
            {
                'id': user.id,
                'matricule': user.matricule,
                'nom_complet': user.get_full_name(),
                'service': user.get_service_path(),
                'droits': user.get_droits_display()
            }
            for user in users
        ]
        
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
    API endpoint optimisée pour récupérer les détails d'un service.
    """
    try:
        service = get_object_or_404(
            Service.objects.prefetch_related(
                Prefetch(
                    'validateurs',
                    queryset=ValidateurService.objects.filter(actif=True).select_related(
                        'validateur', 'audit_source'
                    )
                )
            ), 
            pk=service_id
        )
        
        audit_sources = AuditSource.objects.all().order_by('name')
        
        # Créer un dictionnaire des validateurs par source et niveau
        validateurs_by_source = {}
        for vs in service.validateurs.all():
            if vs.audit_source.id not in validateurs_by_source:
                validateurs_by_source[vs.audit_source.id] = {}
            validateurs_by_source[vs.audit_source.id][vs.niveau] = vs
        
        service_data = {
            'id': service.id,
            'nom': service.nom,
            'code': service.code,
            'audit_sources': []
        }
        
        for audit_source in audit_sources:
            source_validators = validateurs_by_source.get(audit_source.id, {})
            
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
                    }
                ] if (vs := source_validators.get(1)) else [],
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
                    }
                ] if (vs := source_validators.get(2)) else [],
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
                    }
                ] if (vs := source_validators.get(3)) else []
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
    Retourne des statistiques optimisées sur la configuration du workflow.
    """
    try:
        stats = {
            'total_services': Service.objects.filter(sous_services__isnull=True).count(),
            'services_avec_valideurs': ValidateurService.objects.values('service').distinct().count(),
            'total_assignations': ValidateurService.objects.filter(actif=True).count(),
            'assignations_par_niveau': dict(
                ValidateurService.objects.filter(actif=True).values('niveau').annotate(
                    count=models.Count('id')
                ).values_list('niveau', 'count')
            )
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