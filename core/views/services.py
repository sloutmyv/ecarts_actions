"""
Vues pour la gestion des services et de l'organisation hiérarchique.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.db import transaction
from datetime import datetime
import json
from ..models import Service


def services_list(request):
    """
    Vue liste des services avec affichage hiérarchique.
    """
    services_racines = Service.objects.filter(parent=None).order_by('nom')
    context = {
        'services_racines': services_racines,
        'page_title': 'Gestion des Services'
    }
    return render(request, 'core/services/list.html', context)


def service_detail(request, pk):
    """
    Vue détail d'un service avec ses sous-services.
    """
    service = get_object_or_404(Service, pk=pk)
    sous_services = service.sous_services.order_by('nom')
    context = {
        'service': service,
        'sous_services': sous_services,
        'breadcrumb': service.get_chemin_hierarchique().split(' > ')
    }
    return render(request, 'core/services/detail.html', context)


def service_create(request):
    """
    Vue création d'un nouveau service.
    Supporte les requêtes HTMX pour affichage en modal.
    """
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
    
    services = Service.objects.select_related('parent').order_by('nom')
    context = {
        'services': services,
        'page_title': 'Créer un Service'
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/services/form_modal.html', context)
    return render(request, 'core/services/form.html', context)


def service_edit(request, pk):
    """
    Vue modification d'un service existant.
    Supporte les requêtes HTMX pour affichage en modal.
    """
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
    
    services = Service.objects.exclude(pk=service.pk).select_related('parent').order_by('nom')
    context = {
        'service': service,
        'services': services,
        'page_title': f'Modifier {service.nom}'
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/services/form_modal.html', context)
    return render(request, 'core/services/form.html', context)


@require_POST
def service_delete(request, pk):
    """
    Vue suppression d'un service.
    Vérifie qu'il n'y a pas de sous-services avant suppression.
    """
    service = get_object_or_404(Service, pk=pk)
    
    if service.sous_services.exists():
        message = f'Impossible de supprimer "{service.nom}" car il contient des sous-services.'
        if request.headers.get('HX-Request'):
            # Pour HTMX, utiliser un template dédié pour la notification
            from django.template.loader import render_to_string
            notification_html = render_to_string('core/services/notification_error.html', {
                'message': message
            })
            response = HttpResponse(notification_html)
            response['HX-Swap'] = 'beforeend'
            response['HX-Target'] = 'body'
            return response
        else:
            messages.error(request, message)
    else:
        nom_service = service.nom
        service.delete()
        message = f'Le service "{nom_service}" a été supprimé avec succès.'
        if request.headers.get('HX-Request'):
            # Pour HTMX, recharger la liste des services
            response = HttpResponse('')
            response['HX-Trigger'] = 'serviceDeleted'
            return response
        else:
            messages.success(request, message)
    
    return redirect('services_list')


@staff_member_required
def export_services_json(request):
    """
    Exporte tous les services en JSON avec nommage automatique.
    """
    services = Service.objects.all().select_related('parent').order_by('nom')
    
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
    """
    Importe des services depuis un fichier JSON.
    Import destructif qui remplace toute la base de données existante.
    """
    if request.method == 'POST':
        json_file = request.FILES.get('json_file')
        
        if not json_file:
            messages.error(request, 'Veuillez sélectionner un fichier JSON.')
            return redirect('import_services_form')
        
        if not json_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('import_services_form')
        
        try:
            # Lire et parser le fichier JSON
            file_content = json_file.read().decode('utf-8')
            json_data = json.loads(file_content)
            
            # Vérifier la structure du fichier
            if 'data' not in json_data:
                messages.error(request, 'Structure JSON invalide : clé "data" manquante.')
                return redirect('import_services_form')
            
            services_data = json_data['data']
            
            # Statistiques d'import
            created_count = 0
            errors = []
            
            with transaction.atomic():
                # ÉTAPE 1: SUPPRIMER TOUS LES SERVICES EXISTANTS
                deleted_count = Service.objects.count()
                Service.objects.all().delete()
                
                # ÉTAPE 2: CRÉER UN MAPPING ID ANCIEN -> NOUVEAU SERVICE
                id_mapping = {}
                
                # Trier les services par niveau hiérarchique (parents d'abord)
                services_data_sorted = sorted(services_data, key=lambda x: 0 if x.get('parent_id') is None else 1)
                
                # ÉTAPE 3: CRÉER TOUS LES SERVICES EN DEUX PASSES
                # Première passe : créer tous les services sans parent
                for service_data in services_data_sorted:
                    try:
                        old_id = service_data.get('id')
                        nom = service_data.get('nom', 'N/A')
                        code = service_data.get('code', 'N/A')
                        
                        # Créer le service sans parent d'abord
                        service = Service.objects.create(
                            nom=nom,
                            code=code,
                            parent=None  # Parent sera défini en deuxième passe
                        )
                        
                        # Mapper l'ancien ID vers le nouveau service
                        if old_id:
                            id_mapping[old_id] = service
                        
                        created_count += 1
                        
                    except Exception as e:
                        error_msg = f"Erreur pour le service {service_data.get('code', 'N/A')}: {str(e)}"
                        errors.append(error_msg)
                
                # Deuxième passe : définir les relations parent-enfant
                for service_data in services_data_sorted:
                    try:
                        old_id = service_data.get('id')
                        parent_id = service_data.get('parent_id')
                        
                        if old_id in id_mapping and parent_id and parent_id in id_mapping:
                            service = id_mapping[old_id]
                            parent_service = id_mapping[parent_id]
                            service.parent = parent_service
                            service.save()
                            
                    except Exception as e:
                        error_msg = f"Erreur de relation parent pour le service {service_data.get('code', 'N/A')}: {str(e)}"
                        errors.append(error_msg)
            
            # Messages de résultat
            if created_count:
                messages.success(
                    request, 
                    f'Import terminé : {deleted_count} services supprimés, {created_count} services importés depuis le fichier JSON.'
                )
            
            if errors:
                for error in errors[:5]:  # Afficher max 5 erreurs
                    messages.error(request, error)
                if len(errors) > 5:
                    messages.error(request, f'... et {len(errors) - 5} autres erreurs.')
            
            # Rediriger vers la page admin des services après un import réussi
            return redirect('/admin/core/service/')
            
        except json.JSONDecodeError:
            messages.error(request, 'Fichier JSON invalide.')
            return redirect('import_services_form')
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'import : {str(e)}')
            return redirect('import_services_form')
    
    # Si GET, afficher le formulaire d'import
    return render(request, 'admin/core/service/import_form.html')


@staff_member_required  
def import_services_form(request):
    """
    Affiche le formulaire d'import des services.
    """
    return render(request, 'admin/core/service/import_form.html')