from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.core import serializers
from django.db import transaction
from datetime import datetime
import json
from .models import Service

def dashboard(request):
    # Données simulées pour le tableau de bord
    context = {
        'user_stats': {
            'total_ecarts': 24,
            'ecarts_en_cours': 8,
            'ecarts_resolus': 16,
            'plans_actions': 12,
        },
        'recent_ecarts': [
            {
                'id': 1,
                'title': 'Non-conformité process qualité',
                'status': 'En cours',
                'priority': 'Haute',
                'date': '2024-01-28',
                'assignee': 'Marie Dupont'
            },
            {
                'id': 2,
                'title': 'Écart documentaire ISO 9001',
                'status': 'Nouveau',
                'priority': 'Moyenne',
                'date': '2024-01-27',
                'assignee': 'Jean Martin'
            },
            {
                'id': 3,
                'title': 'Incident sécurité atelier',
                'status': 'Résolu',
                'priority': 'Haute',
                'date': '2024-01-26',
                'assignee': 'Paul Bernard'
            },
        ],
        'notifications': [
            {
                'type': 'warning',
                'message': 'Vous avez 3 écarts en attente de validation',
                'time': 'Il y a 2h'
            },
            {
                'type': 'info',
                'message': 'Nouveau plan d\'action assigné',
                'time': 'Il y a 4h'
            },
            {
                'type': 'success',
                'message': 'Écart #15 résolu avec succès',
                'time': 'Hier'
            },
        ]
    }
    return render(request, 'core/dashboard.html', context)


def services_list(request):
    services_racines = Service.objects.filter(parent=None).order_by('nom')
    context = {
        'services_racines': services_racines,
        'page_title': 'Gestion des Services'
    }
    return render(request, 'core/services_list.html', context)


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    sous_services = service.sous_services.order_by('nom')
    context = {
        'service': service,
        'sous_services': sous_services,
        'breadcrumb': service.get_chemin_hierarchique().split(' > ')
    }
    return render(request, 'core/service_detail.html', context)


def service_create(request):
    if request.method == 'POST':
        try:
            service = Service(
                nom=request.POST.get('nom'),
                code=request.POST.get('code')
            )
            
            parent_id = request.POST.get('parent')
            if parent_id:
                service.parent = get_object_or_404(Service, pk=parent_id)
            
            service.full_clean()
            service.save()
            
            messages.success(request, f'Le service "{service.nom}" a été créé avec succès.')
            
            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'success': True,
                    'message': f'Service "{service.nom}" créé avec succès',
                    'redirect': reverse('services_list')
                })
            return redirect('services_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': False, 'error': str(e)})
    
    services = Service.objects.order_by('nom')
    context = {
        'services': services,
        'page_title': 'Créer un Service'
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/service_form_modal.html', context)
    return render(request, 'core/service_form.html', context)


def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        try:
            service.nom = request.POST.get('nom')
            service.code = request.POST.get('code')
            
            parent_id = request.POST.get('parent')
            if parent_id and int(parent_id) != service.pk:
                service.parent = get_object_or_404(Service, pk=parent_id)
            elif not parent_id:
                service.parent = None
            
            service.full_clean()
            service.save()
            
            messages.success(request, f'Le service "{service.nom}" a été modifié avec succès.')
            
            if request.headers.get('HX-Request'):
                return JsonResponse({
                    'success': True,
                    'message': f'Service "{service.nom}" modifié avec succès',
                    'redirect': reverse('services_list')
                })
            return redirect('services_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': False, 'error': str(e)})
    
    services = Service.objects.exclude(pk=service.pk).order_by('nom')
    context = {
        'service': service,
        'services': services,
        'page_title': f'Modifier {service.nom}'
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/service_form_modal.html', context)
    return render(request, 'core/service_form.html', context)


@require_POST
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    
    if service.sous_services.exists():
        message = f'Impossible de supprimer "{service.nom}" car il contient des sous-services.'
        messages.error(request, message)
        if request.headers.get('HX-Request'):
            return JsonResponse({'success': False, 'error': message})
    else:
        nom_service = service.nom
        service.delete()
        message = f'Le service "{nom_service}" a été supprimé avec succès.'
        messages.success(request, message)
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': True,
                'message': message,
                'redirect': reverse('services_list')
            })
    
    return redirect('services_list')




@staff_member_required
def export_services_json(request):
    """Exporte tous les services en JSON avec nommage automatique"""
    services = Service.objects.all().select_related('parent')
    
    # Préparer les données pour l'export
    data = []
    for service in services:
        service_data = {
            'id': service.id,
            'nom': service.nom,
            'code': service.code,
            'parent_id': service.parent.id if service.parent else None,
            'parent_code': service.parent.code if service.parent else None,
            'created_at': service.created_at.isoformat() if service.created_at else None,
            'updated_at': service.updated_at.isoformat() if service.updated_at else None,
        }
        data.append(service_data)
    
    # Préparer le fichier JSON avec métadonnées
    export_data = {
        'model': 'Service',
        'export_date': datetime.now().isoformat(),
        'total_records': len(data),
        'data': data
    }
    
    # Créer la réponse HTTP avec le fichier JSON
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    
    # Nom du fichier avec convention : modele_YYMMDD.json
    filename = f"Service_{datetime.now().strftime('%y%m%d')}.json"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    messages.success(request, f'Export terminé : {len(data)} services exportés dans {filename}')
    return response


@staff_member_required
def import_services_json(request):
    """Importe des services depuis un fichier JSON"""
    if request.method == 'POST':
        json_file = request.FILES.get('json_file')
        
        if not json_file:
            messages.error(request, 'Veuillez sélectionner un fichier JSON.')
            return redirect('/admin/core/service/')
        
        if not json_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('/admin/core/service/')
        
        try:
            # Lire et parser le fichier JSON
            file_content = json_file.read().decode('utf-8')
            json_data = json.loads(file_content)
            
            # Vérifier la structure du fichier
            if 'data' not in json_data:
                messages.error(request, 'Structure JSON invalide : clé "data" manquante.')
                return redirect('/admin/core/service/')
            
            services_data = json_data['data']
            
            # Statistiques d'import
            created_count = 0
            updated_count = 0
            errors = []
            
            with transaction.atomic():
                # Trier les services par niveau hiérarchique (parents d'abord)
                services_data_sorted = sorted(services_data, key=lambda x: 0 if x.get('parent_id') is None else 1)
                
                for service_data in services_data_sorted:
                    try:
                        # Chercher un service existant par code
                        existing_service = Service.objects.filter(code=service_data['code']).first()
                        
                        if existing_service:
                            # Mettre à jour le service existant
                            existing_service.nom = service_data['nom']
                            if service_data.get('parent_id'):
                                parent = Service.objects.filter(id=service_data['parent_id']).first()
                                existing_service.parent = parent
                            else:
                                existing_service.parent = None
                            existing_service.save()
                            updated_count += 1
                        else:
                            # Créer un nouveau service
                            parent = None
                            if service_data.get('parent_id'):
                                parent = Service.objects.filter(id=service_data['parent_id']).first()
                            
                            service = Service.objects.create(
                                nom=service_data['nom'],
                                code=service_data['code'],
                                parent=parent
                            )
                            created_count += 1
                            
                    except Exception as e:
                        errors.append(f"Erreur pour le service {service_data.get('code', 'N/A')}: {str(e)}")
            
            # Messages de résultat
            if created_count or updated_count:
                messages.success(
                    request, 
                    f'Import terminé : {created_count} services créés, {updated_count} services mis à jour.'
                )
            
            if errors:
                for error in errors[:5]:  # Afficher max 5 erreurs
                    messages.error(request, error)
                if len(errors) > 5:
                    messages.error(request, f'... et {len(errors) - 5} autres erreurs.')
            
        except json.JSONDecodeError:
            messages.error(request, 'Fichier JSON invalide.')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'import : {str(e)}')
        
        return redirect('/admin/core/service/')
    
    # Afficher le formulaire d'import
    return render(request, 'admin/core/service/import_form.html')


@staff_member_required
def import_services_form(request):
    """Affiche le formulaire d'import"""
    return render(request, 'admin/core/service/import_form.html')
