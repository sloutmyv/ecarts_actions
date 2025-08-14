"""
Vues pour le tableau de bord principal de l'application.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Case, When, IntegerField
from ..models import GapReport, Gap, Notification
from ..services.validation_service import ValidationService


@login_required
def dashboard(request):
    """
    Vue principale du tableau de bord avec statistiques et activités récentes.
    """
    user = request.user
    
    # Statistiques des déclarations créées par l'utilisateur
    user_gap_reports = GapReport.objects.filter(declared_by=user)
    
    # Compter les écarts (is_gap=True) et événements (is_gap=False) créés par l'utilisateur
    gaps_created = Gap.objects.filter(
        gap_report__declared_by=user,
        gap_type__is_gap=True
    )
    events_created = Gap.objects.filter(
        gap_report__declared_by=user,
        gap_type__is_gap=False
    )
    
    # Compter par statut pour les écarts uniquement
    gaps_by_status = gaps_created.aggregate(
        declared=Count('id', filter=Q(status='declared')),
        retained=Count('id', filter=Q(status='retained')),
        rejected=Count('id', filter=Q(status='rejected')),
    )
    
    # Notifications non lues uniquement (5 dernières)
    notifications = Notification.objects.filter(
        user=user,
        is_read=False
    ).select_related('gap', 'gap__gap_report').order_by('-created_at')[:5]
    
    # Nombre de notifications non lues
    unread_notifications = Notification.objects.filter(
        user=user, 
        is_read=False
    ).count()
    
    # Historique des actions récentes de l'utilisateur (actions + notifications lues)
    from ..models.gaps import HistoriqueModification
    from django.utils import timezone
    from datetime import timedelta
    
    # Actions récentes de l'utilisateur (10 dernières pour avoir plus de choix)
    user_actions = HistoriqueModification.objects.filter(
        utilisateur=user
    ).select_related('gap_report', 'gap').order_by('-created_at')[:10]
    
    # Notifications lues récemment (3 derniers jours, 10 max)
    three_days_ago = timezone.now() - timedelta(days=3)
    read_notifications = Notification.objects.filter(
        user=user,
        is_read=True,
        read_at__gte=three_days_ago
    ).select_related('gap', 'gap__gap_report').order_by('-read_at')[:10]
    
    # Mélanger les actions et notifications lues, prendre les 5 plus récentes
    history_items = []
    
    # Ajouter les actions avec un type 'action'
    for action in user_actions:
        history_items.append({
            'type': 'action',
            'timestamp': action.created_at,
            'data': action
        })
    
    # Ajouter les notifications lues avec un type 'notification'
    for notification in read_notifications:
        history_items.append({
            'type': 'notification',
            'timestamp': notification.read_at,
            'data': notification
        })
    
    # Trier par timestamp décroissant et prendre les 5 plus récents
    history_items.sort(key=lambda x: x['timestamp'], reverse=True)
    user_history = history_items[:5]
    
    # Écarts en attente de validation par cet utilisateur
    pending_validations = ValidationService.get_pending_validations(user)
    
    context = {
        'user_stats': {
            'total_evenements': gaps_created.count() + events_created.count(),  # Total événements (écarts + non-écarts)
            'total_ecarts': gaps_created.count(),  # Détail écarts uniquement
            'evenements_non_ecarts': events_created.count(),  # Événements qui ne sont pas des écarts
            'ecarts_declares': gaps_by_status['declared'],
            'ecarts_retenus': gaps_by_status['retained'],
            'ecarts_non_retenus': gaps_by_status['rejected'],
        },
        'notifications': notifications,
        'unread_notifications': unread_notifications,
        'user_history': user_history,
        'pending_validations': pending_validations[:5],  # 5 premiers écarts à valider
        'pending_validations_count': len(pending_validations),
    }
    return render(request, 'core/dashboard/dashboard.html', context)