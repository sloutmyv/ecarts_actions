"""
Vues pour la gestion des utilisateurs.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import datetime
import json
from ..models import Service

User = get_user_model()


def user_can_manage_users(user):
    """Vérification que l'utilisateur peut gérer les utilisateurs."""
    return user.is_authenticated and user.can_manage_users()


@login_required
@user_passes_test(user_can_manage_users)
def users_list(request):
    """
    Vue liste des utilisateurs avec filtrage par service et tri.
    Affiche seulement les utilisateurs actifs dans l'application principale.
    Les utilisateurs inactifs ne sont visibles que dans l'admin Django.
    """
    # Afficher seulement les utilisateurs actifs dans l'application principale
    users = User.objects.filter(actif=True).select_related('service')
        
    services = Service.objects.filter(actif=True).order_by('nom')  # Seuls services actifs dans les filtres
    
    # Filtrage par service si spécifié
    service_filter = request.GET.get('service')
    if service_filter:
        users = users.filter(service_id=service_filter)
    
    # Gestion du tri
    sort_by = request.GET.get('sort', 'nom')  # Tri par défaut par nom
    order = request.GET.get('order', 'asc')   # Ordre par défaut croissant
    
    # Définir les champs de tri autorisés et leurs correspondances
    sort_fields = {
        'nom': 'nom',
        'prenom': 'prenom', 
        'matricule': 'matricule',
        'service': 'service__nom',
        'email': 'email',
        'droits': 'droits'
    }
    
    # Vérifier que le champ de tri est autorisé
    if sort_by in sort_fields:
        sort_field = sort_fields[sort_by]
        
        # Appliquer l'ordre (croissant ou décroissant)
        if order == 'desc':
            sort_field = '-' + sort_field
            
        users = users.order_by(sort_field, 'nom', 'prenom')  # Tri secondaire par nom/prénom
    else:
        # Tri par défaut
        users = users.order_by('nom', 'prenom')
    
    # Déterminer l'ordre inverse pour les liens de tri
    next_order = 'desc' if order == 'asc' else 'asc'
    
    context = {
        'users': users,
        'services': services,
        'selected_service': service_filter,
        'page_title': 'Gestion des Utilisateurs',
        'current_sort': sort_by,
        'current_order': order,
        'next_order': next_order,
    }
    return render(request, 'core/users/list.html', context)


@login_required
@user_passes_test(user_can_manage_users)
def user_detail(request, pk):
    """
    Vue détail d'un utilisateur.
    Ne permet d'accéder qu'aux utilisateurs actifs.
    """
    user = get_object_or_404(User, pk=pk, actif=True)  # Utilisateur doit être actif
    context = {
        'user_detail': user,  # Renommé pour éviter le conflit avec request.user
        'page_title': f'Détail - {user.get_full_name()}'
    }
    return render(request, 'core/users/detail.html', context)


@login_required
@user_passes_test(user_can_manage_users)
def user_create(request):
    """
    Vue création d'un nouvel utilisateur.
    Supporte les requêtes HTMX pour affichage en modal.
    """
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            matricule = request.POST.get('matricule', '').upper()
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            email = request.POST.get('email') or None
            droits = request.POST.get('droits')
            service_id = request.POST.get('service')
            
            # Création de l'utilisateur avec mot de passe par défaut
            user = User(
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                email=email,
                droits=droits
            )
            
            # Définir le mot de passe par défaut AVANT la validation
            user.set_password('azerty')
            user.must_change_password = True
            
            # Association au service si spécifié
            if service_id:
                user.service = get_object_or_404(Service, pk=service_id)
            
            # Validation et sauvegarde
            user.full_clean()
            user.save()
            
            messages.success(request, f'L\'utilisateur "{user.get_full_name()}" a été créé avec succès.')
            
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                response = HttpResponse()
                response['HX-Redirect'] = reverse('users_list')
                return response
            return redirect('users_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': False, 'error': str(e)})
    
    # Seuls les services actifs peuvent être assignés aux utilisateurs
    services = Service.objects.filter(actif=True).order_by('nom')
    context = {
        'services': services,
        'droits_choices': User.DROITS_CHOICES,
        'page_title': 'Créer un Utilisateur'
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/users/form_modal.html', context)
    return render(request, 'core/users/form.html', context)


@login_required
@user_passes_test(user_can_manage_users)
def user_edit(request, pk):
    """
    Vue modification d'un utilisateur existant.
    Supporte les requêtes HTMX pour affichage en modal.
    Ne permet d'éditer que les utilisateurs actifs.
    """
    user_to_edit = get_object_or_404(User, pk=pk, actif=True)  # Utilisateur doit être actif pour être éditable
    
    if request.method == 'POST':
        try:
            # Récupération des données du formulaire
            user_to_edit.matricule = request.POST.get('matricule', '').upper()
            user_to_edit.nom = request.POST.get('nom')
            user_to_edit.prenom = request.POST.get('prenom')
            user_to_edit.email = request.POST.get('email') or None
            user_to_edit.droits = request.POST.get('droits')
            
            # Association au service
            service_id = request.POST.get('service')
            if service_id:
                user_to_edit.service = get_object_or_404(Service, pk=service_id)
            else:
                user_to_edit.service = None
            
            # Validation et sauvegarde
            user_to_edit.full_clean()
            user_to_edit.save()
            
            messages.success(request, f'L\'utilisateur "{user_to_edit.get_full_name()}" a été modifié avec succès.')
            
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                response = HttpResponse()
                response['HX-Redirect'] = reverse('users_list')
                return response
            return redirect('users_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': False, 'error': str(e)})
    
    # Seuls les services actifs peuvent être assignés aux utilisateurs
    services = Service.objects.filter(actif=True).order_by('nom')
    context = {
        'user_to_edit': user_to_edit,
        'services': services,
        'droits_choices': User.DROITS_CHOICES,
        'page_title': f'Modifier {user_to_edit.get_full_name()}'
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/users/form_modal.html', context)
    return render(request, 'core/users/form.html', context)


@login_required 
@user_passes_test(user_can_manage_users)
@require_POST
def user_delete(request, pk):
    """
    Vue suppression d'un utilisateur.
    Affiche une modale de confirmation avant suppression.
    Ne permet de supprimer que les utilisateurs actifs.
    """
    user_to_delete = get_object_or_404(User, pk=pk, actif=True)  # Utilisateur doit être actif pour être supprimable
    
    # Empêcher la suppression de son propre compte
    if user_to_delete == request.user:
        message = 'Vous ne pouvez pas supprimer votre propre compte.'
        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            from django.middleware.csrf import get_token
            notification_html = render_to_string('core/users/notification_error.html', {
                'message': message,
                'csrf_token': get_token(request)
            })
            response = HttpResponse(notification_html)
            response['HX-Retarget'] = '#modal-container'
            response['HX-Reswap'] = 'innerHTML'
            return response
        else:
            messages.error(request, message)
    else:
        # Afficher la modale de confirmation
        message = f'Êtes-vous sûr de vouloir supprimer l\'utilisateur "{user_to_delete.get_full_name()}" ?'
        
        if request.headers.get('HX-Request'):
            from django.template.loader import render_to_string
            from django.middleware.csrf import get_token
            notification_html = render_to_string('core/users/notification_confirm.html', {
                'message': message,
                'user': user_to_delete,
                'csrf_token': get_token(request)
            })
            response = HttpResponse(notification_html)
            response['HX-Retarget'] = '#modal-container'
            response['HX-Reswap'] = 'innerHTML'
            return response
        else:
            # Pour les requêtes non-HTMX, supprimer directement (ancien comportement)
            nom_complet = user_to_delete.get_full_name()
            user_to_delete.delete()
            messages.success(request, f'L\'utilisateur "{nom_complet}" a été supprimé avec succès.')
    
    return redirect('users_list')


@login_required
@user_passes_test(user_can_manage_users)
@require_POST
def user_delete_confirm(request, pk):
    """
    Confirmation définitive de suppression d'un utilisateur.
    """
    user_to_delete = get_object_or_404(User, pk=pk)
    
    # Empêcher la suppression de son propre compte (sécurité supplémentaire)
    if user_to_delete == request.user:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('users_list')
    
    # Supprimer l'utilisateur
    nom_complet = user_to_delete.get_full_name()
    user_to_delete.delete()
    
    message = f'L\'utilisateur "{nom_complet}" a été supprimé avec succès.'
    
    if request.headers.get('HX-Request'):
        # Pour HTMX, retourner un contenu vide pour déclencher le rechargement
        response = HttpResponse('')
        response['HX-Trigger'] = 'userDeleted'
        return response
    else:
        messages.success(request, message)
    
    return redirect('users_list')


@login_required
@user_passes_test(user_can_manage_users)
@require_POST
def user_reset_password(request, pk):
    """
    Vue pour réinitialiser le mot de passe d'un utilisateur à "azerty".
    """
    user_to_reset = get_object_or_404(User, pk=pk)
    
    try:
        user_to_reset.set_password('azerty')
        user_to_reset.must_change_password = True
        user_to_reset.save()
        
        message = f'Le mot de passe de "{user_to_reset.get_full_name()}" a été réinitialisé à "azerty".'
        messages.success(request, message)
        
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': True,
                'message': message
            })
            
    except Exception as e:
        message = f'Erreur lors de la réinitialisation : {str(e)}'
        messages.error(request, message)
        
        if request.headers.get('HX-Request'):
            return JsonResponse({'success': False, 'error': message})
    
    return redirect('users_list')


# La fonction user_toggle_active a été supprimée car les utilisateurs inactifs 
# ne doivent plus être visibles dans l'application principale.
# L'activation/désactivation se fait uniquement via l'admin Django.


@login_required
@user_passes_test(user_can_manage_users)
def export_users_json(request):
    """
    Export tous les utilisateurs au format JSON.
    """
    
    # Récupérer tous les utilisateurs avec leurs services
    users = User.objects.select_related('service').order_by('matricule')
    
    # Préparer les données pour l'export
    data = []
    for user in users:
        user_data = {
            'id': user.id,
            'matricule': user.matricule,
            'nom': user.nom,
            'prenom': user.prenom,
            'email': user.email or None,
            'droits': user.droits,
            'service_id': user.service.id if user.service else None,
            'service_code': user.service.code if user.service else None,
            'actif': user.actif,
            'must_change_password': user.must_change_password,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
            'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
        data.append(user_data)
    
    # Créer la structure d'export
    export_data = {
        'model': 'User',
        'export_date': datetime.now().isoformat(),
        'total_records': len(data),
        'data': data
    }
    
    # Générer le nom de fichier avec la date
    filename = f"Users_{datetime.now().strftime('%y%m%d')}.json"
    
    # Créer la réponse HTTP avec le fichier JSON
    response = HttpResponse(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Message de succès
    messages.success(request, f'Export terminé : {len(data)} utilisateurs exportés dans {filename}')
    
    return response


@login_required
@user_passes_test(user_can_manage_users)
def import_users_json(request):
    """
    Import des utilisateurs depuis un fichier JSON.
    ⚠️ ATTENTION : Cette opération supprime TOUS les utilisateurs existants.
    """
    
    if request.method == 'POST':
        if 'json_file' not in request.FILES:
            messages.error(request, 'Aucun fichier sélectionné.')
            return redirect('import_users_form')
        
        json_file = request.FILES['json_file']
        if not json_file.name.endswith('.json'):
            messages.error(request, 'Le fichier doit être au format JSON.')
            return redirect('import_users_form')
        
        try:
            # Lire et parser le JSON
            file_content = json_file.read().decode('utf-8')
            try:
                data = json.loads(file_content)
            except json.JSONDecodeError as e:
                messages.error(request, f'Fichier JSON invalide : {str(e)}')
                return redirect('import_users_form')
            
            # Vérifier la structure du fichier
            if not isinstance(data, dict) or 'data' not in data:
                messages.error(request, 'Structure de fichier JSON invalide. Le fichier doit contenir une clé "data".')
                return redirect('import_users_form')
            
            users_data = data['data']
            if not isinstance(users_data, list):
                messages.error(request, 'La clé "data" doit contenir une liste d\'utilisateurs.')
                return redirect('import_users_form')
            
            # Statistiques d'import
            deleted_count = 0
            created_count = 0
            
            # Transaction atomique pour assurer la cohérence
            try:
                with transaction.atomic():
                    # Étape 1: Supprimer TOUS les utilisateurs existants (sauf l'utilisateur actuel)
                    current_user = request.user
                    existing_users = User.objects.exclude(pk=current_user.pk)
                    deleted_count = existing_users.count()
                    existing_users.delete()
                    
                    # Étape 2: Créer les utilisateurs depuis le JSON
                    services_map = {}  # Cache pour les services
                    
                    for user_data in users_data:
                        # Éviter de recréer l'utilisateur actuel
                        if user_data.get('id') == current_user.pk or user_data.get('matricule') == current_user.matricule:
                            continue
                            
                        # Récupérer ou créer le service si spécifié
                        service = None
                        if user_data.get('service_code'):
                            service_code = user_data['service_code']
                            if service_code not in services_map:
                                try:
                                    services_map[service_code] = Service.objects.get(code=service_code)
                                except Service.DoesNotExist:
                                    # Si le service n'existe pas, on ignore cette affectation
                                    services_map[service_code] = None
                            service = services_map[service_code]
                        
                        # Créer l'utilisateur
                        user = User(
                            matricule=user_data.get('matricule'),
                            nom=user_data.get('nom', ''),
                            prenom=user_data.get('prenom', ''),
                            email=user_data.get('email') or '',
                            droits=user_data.get('droits', User.USER),
                            service=service,
                            must_change_password=True,  # Toujours True pour les imports
                            is_staff=user_data.get('is_staff', False),
                            is_superuser=user_data.get('is_superuser', False),
                        )
                        
                        # Définir le mot de passe par défaut
                        user.set_password('azerty')
                        
                        # Sauvegarder
                        user.full_clean()  # Validation
                        user.save()
                        created_count += 1
                
                # Message de succès
                messages.success(
                    request,
                    f'Import terminé : {deleted_count} utilisateurs supprimés, {created_count} utilisateurs importés depuis le fichier JSON.'
                )
                
                # Rediriger vers la page admin des utilisateurs après un import réussi
                return redirect('admin:core_user_changelist')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'import : {str(e)}')
                return redirect('import_users_form')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'import : {str(e)}')
            return redirect('import_users_form')
    
    # Si GET, afficher le formulaire d'import
    return render(request, 'admin/core/user/import_form.html')


@login_required
@user_passes_test(user_can_manage_users)
def import_users_form(request):
    """
    Affiche le formulaire d'import des utilisateurs.
    """
    return render(request, 'admin/core/user/import_form.html')


