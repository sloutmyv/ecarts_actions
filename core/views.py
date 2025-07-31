from django.shortcuts import render
from django.http import HttpResponse

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
