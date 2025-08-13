"""
Vues pour la validation des écarts et la gestion des notifications.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Max
from ..models import Gap, Notification, GapValidation
from ..services.validation_service import ValidationService
from ..signals import set_current_user


@login_required
def validate_gap(request, gap_id):
    """
    Vue pour valider ou rejeter un écart.
    """
    gap = get_object_or_404(Gap, id=gap_id, status='declared', gap_type__is_gap=True)
    
    # Vérifier que l'utilisateur peut valider cet écart
    pending_gaps = ValidationService.get_pending_validations(request.user)
    if gap not in pending_gaps:
        messages.error(request, "Vous n'êtes pas autorisé à valider cet écart.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'approved' ou 'rejected'
        comment = request.POST.get('comment', '').strip()
        
        if action not in ['approved', 'rejected']:
            messages.error(request, "Action invalide.")
            return redirect('validate_gap', gap_id=gap.id)
        
        try:
            set_current_user(request.user)
            
            with transaction.atomic():
                # Effectuer la validation
                is_final = ValidationService.validate_gap(
                    gap=gap,
                    validator=request.user,
                    action=action,
                    comment=comment
                )
                
                # Marquer comme lues toutes les notifications de validation pour cet écart et ce validateur
                # uniquement APRÈS une validation réussie
                from django.utils import timezone
                updated_notifications = Notification.objects.filter(
                    user=request.user,
                    gap=gap,
                    type='validation_request',
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                
                # Marquer aussi toutes les autres notifications non lues pour ce gap et cet utilisateur
                all_updated = Notification.objects.filter(
                    user=request.user,
                    gap=gap,
                    is_read=False
                ).update(
                    is_read=True,
                    read_at=timezone.now()
                )
                
                # Messages de succès
                if action == 'approved':
                    if is_final:
                        messages.success(request, f"Écart {gap.gap_number} approuvé et retenu.")
                    else:
                        messages.success(request, f"Écart {gap.gap_number} approuvé. Envoyé au niveau suivant.")
                else:
                    messages.success(request, f"Écart {gap.gap_number} rejeté.")
                
                return redirect('dashboard')
                
        except Exception as e:
            messages.error(request, f"Erreur lors de la validation : {e}")
    
    context = {
        'gap': gap,
    }
    return render(request, 'core/validation/validate_gap.html', context)


@login_required
def notifications_list(request):
    """
    Vue pour afficher les notifications de l'utilisateur.
    """
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('gap', 'gap__gap_report', 'gap__gap_type').order_by('-created_at')
    
    # Marquer les notifications comme lues si demandé
    mark_read = request.GET.get('mark_read')
    if mark_read:
        if mark_read == 'all':
            notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        else:
            try:
                notification_id = int(mark_read)
                notification = notifications.filter(id=notification_id, is_read=False).first()
                if notification:
                    notification.mark_as_read()
            except (ValueError, TypeError):
                pass
    
    context = {
        'notifications': notifications[:50],  # Limiter à 50 notifications
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'core/validation/notifications.html', context)


@login_required 
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """
    Marque une notification comme lue via AJAX.
    Les notifications de validation ne peuvent pas être marquées comme lues manuellement.
    """
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            user=request.user
        )
        
        # Empêcher le marquage manuel des notifications de validation
        if notification.type == 'validation_request':
            return JsonResponse({
                'success': False,
                'message': 'Les notifications de validation ne peuvent être marquées comme lues qu\'en effectuant la validation.'
            }, status=403)
        
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marquée comme lue'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def pending_validations(request):
    """
    Vue pour afficher les écarts en attente de validation.
    """
    pending_gaps = ValidationService.get_pending_validations(request.user)
    
    context = {
        'pending_gaps': pending_gaps,
        'pending_count': len(pending_gaps),
    }
    return render(request, 'core/validation/pending_validations.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def change_gap_status(request, gap_id):
    """
    Vue pour permettre aux validateurs de changer le statut des écarts sur leur périmètre.
    """
    from ..models.workflow import ValidateurService
    
    gap = get_object_or_404(Gap, id=gap_id, gap_type__is_gap=True)
    
    # Vérifier que l'utilisateur peut modifier le statut de cet écart
    can_modify = False
    
    # Les administrateurs peuvent toujours modifier
    if request.user.droits in ['SA', 'AD']:
        can_modify = True
    else:
        # Vérifier si l'utilisateur est validateur du niveau le plus élevé pour ce service/source d'audit
        validator_assignments = ValidateurService.get_services_validateur(
            request.user, actif_seulement=True
        ).filter(
            service=gap.gap_report.service,
            audit_source=gap.gap_report.audit_source
        )
        
        if validator_assignments.exists():
            # Récupérer le niveau maximum pour cette combinaison service/source d'audit
            max_level = ValidateurService.get_validateurs_service(
                service=gap.gap_report.service,
                audit_source=gap.gap_report.audit_source,
                actif_seulement=True
            ).aggregate(max_niveau=Max('niveau'))['max_niveau']
            
            # Vérifier si l'utilisateur est validateur au niveau maximum
            user_max_level = validator_assignments.aggregate(
                user_max_niveau=Max('niveau')
            )['user_max_niveau']
            
            # L'utilisateur peut modifier seulement s'il est au niveau maximum
            if user_max_level == max_level:
                can_modify = True
    
    if not can_modify:
        # Message d'erreur personnalisé selon le contexte
        if request.user.droits not in ['SA', 'AD']:
            validator_assignments = ValidateurService.get_services_validateur(
                request.user, actif_seulement=True
            ).filter(
                service=gap.gap_report.service,
                audit_source=gap.gap_report.audit_source
            )
            
            if validator_assignments.exists():
                messages.error(request, "Seuls les validateurs du niveau le plus élevé peuvent modifier le statut des écarts.")
            else:
                messages.error(request, "Vous n'êtes pas validateur pour ce service et cette source d'audit.")
        else:
            messages.error(request, "Vous n'êtes pas autorisé à modifier le statut de cet écart.")
        
        return redirect('dashboard')
    
    # Définir les statuts disponibles (nécessaire pour le POST et GET)
    status_choices = [
        ('declared', 'Déclaré'),
        ('cancelled', 'Annulé'),
        ('retained', 'Retenu'),
        ('rejected', 'Non retenu'),
        ('closed', 'Clos'),
    ]

    if request.method == 'POST':
        new_status = request.POST.get('status')
        comment = request.POST.get('comment', '').strip()
        
        # Définir les statuts autorisés selon le rôle
        allowed_statuses = []
        
        if request.user.droits in ['SA', 'AD']:
            # Les administrateurs peuvent changer vers n'importe quel statut
            allowed_statuses = ['declared', 'cancelled', 'retained', 'rejected', 'closed']
        else:
            # Les validateurs ont des restrictions selon le statut actuel
            if gap.status == 'declared':
                allowed_statuses = ['retained', 'rejected']
            elif gap.status == 'retained':
                allowed_statuses = ['closed', 'rejected']
            elif gap.status == 'rejected':
                allowed_statuses = ['declared', 'retained']  # Possibilité de réouvrir
            elif gap.status == 'closed':
                allowed_statuses = ['retained']  # Possibilité de réouvrir
        
        if new_status not in allowed_statuses:
            messages.error(request, "Changement de statut non autorisé.")
            return redirect('change_gap_status', gap_id=gap.id)
        
        if new_status == gap.status:
            messages.warning(request, "Le statut est déjà défini sur cette valeur.")
            return redirect('change_gap_status', gap_id=gap.id)
        
        try:
            with transaction.atomic():
                old_status = gap.status
                gap.status = new_status
                gap.save(update_fields=['status', 'updated_at'])
                
                # L'historique est automatiquement créé par le signal post_save
                
                # Créer une entrée dans l'historique des validations pour les changements de statut directs
                if new_status in ['retained', 'rejected', 'closed']:
                    # Déterminer l'action selon le nouveau statut
                    if new_status == 'retained':
                        validation_action = 'approved'
                    elif new_status == 'rejected':
                        validation_action = 'rejected'
                    elif new_status == 'closed':
                        validation_action = 'approved'  # Clôture = validation finale
                    
                    # Déterminer le niveau de validation de l'utilisateur
                    from ..models.workflow import ValidateurService
                    validator_assignments = ValidateurService.get_services_validateur(
                        request.user, actif_seulement=True
                    ).filter(
                        service=gap.gap_report.service,
                        audit_source=gap.gap_report.audit_source
                    )
                    
                    if validator_assignments.exists():
                        user_level = validator_assignments.aggregate(
                            max_niveau=Max('niveau')
                        )['max_niveau']
                        
                        # Créer l'entrée de validation
                        GapValidation.objects.update_or_create(
                            gap=gap,
                            level=user_level,
                            defaults={
                                'validator': request.user,
                                'action': validation_action,
                                'comment': f"Changement de statut direct vers '{gap.get_status_display()}'" + 
                                          (f" - {comment}" if comment else "")
                            }
                        )
                
                # Créer des notifications si nécessaire
                if new_status in ['retained', 'rejected', 'closed']:
                    # Notifier le déclarant du changement de statut
                    Notification.objects.create(
                        user=gap.gap_report.declared_by,
                        gap=gap,
                        type='gap_status_changed',
                        title=f"{gap.gap_number} - Statut modifié",
                        message=f"Le statut de votre événement {gap.gap_number} a été modifié vers '{gap.get_status_display()}' par {request.user.get_full_name()}."
                                f"{f' Commentaire: {comment}' if comment else ''}",
                        priority='normal'
                    )
                
                messages.success(request, f"Statut de l'écart {gap.gap_number} modifié vers '{gap.get_status_display()}'.")
                return redirect('dashboard')
                
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification du statut : {e}")
    
    # Définir les statuts disponibles pour la sélection
    available_statuses = []
    
    if request.user.droits in ['SA', 'AD']:
        # Les administrateurs voient tous les statuts sauf le statut actuel
        available_statuses = [s for s in status_choices if s[0] != gap.status]
    else:
        # Les validateurs ont des restrictions
        if gap.status == 'declared':
            available_statuses = [('retained', 'Retenu'), ('rejected', 'Non retenu')]
        elif gap.status == 'retained':
            available_statuses = [('closed', 'Clos'), ('rejected', 'Non retenu')]
        elif gap.status == 'rejected':
            available_statuses = [('declared', 'Déclaré'), ('retained', 'Retenu')]
        elif gap.status == 'closed':
            available_statuses = [('retained', 'Retenu')]
    
    context = {
        'gap': gap,
        'available_statuses': available_statuses,
        'current_status_display': gap.get_status_display(),
    }
    
    return render(request, 'core/validation/change_gap_status.html', context)