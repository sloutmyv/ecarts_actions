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
    Vue liste des utilisateurs avec filtrage par service.
    """
    users = User.objects.select_related('service').order_by('nom', 'prenom')
    services = Service.objects.all().order_by('nom')
    
    # Filtrage par service si spécifié
    service_filter = request.GET.get('service')
    if service_filter:
        users = users.filter(service_id=service_filter)
    
    context = {
        'users': users,
        'services': services,
        'selected_service': service_filter,
        'page_title': 'Gestion des Utilisateurs'
    }
    return render(request, 'core/users/list.html', context)


@login_required
@user_passes_test(user_can_manage_users)
def user_detail(request, pk):
    """
    Vue détail d'un utilisateur.
    """
    user = get_object_or_404(User, pk=pk)
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
                return JsonResponse({
                    'success': True,
                    'message': f'Utilisateur "{user.get_full_name()}" créé avec succès',
                    'redirect': reverse('users_list')
                })
            return redirect('users_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': False, 'error': str(e)})
    
    services = Service.objects.all().order_by('nom')
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
    """
    user_to_edit = get_object_or_404(User, pk=pk)
    
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
                return JsonResponse({
                    'success': True,
                    'message': f'Utilisateur "{user_to_edit.get_full_name()}" modifié avec succès',
                    'redirect': reverse('users_list')
                })
            return redirect('users_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la modification : {str(e)}')
            if request.headers.get('HX-Request'):
                return JsonResponse({'success': False, 'error': str(e)})
    
    services = Service.objects.all().order_by('nom')
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
    """
    user_to_delete = get_object_or_404(User, pk=pk)
    
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


