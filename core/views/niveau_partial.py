"""
Vue pour retourner le HTML partiel d'un niveau de validation.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from ..models import ValidateurService, Service, AuditSource


@staff_member_required
def get_niveau_partial(request, service_id, audit_source_id, niveau):
    """
    Retourne le HTML partiel d'un niveau de validation spécifique.
    """
    try:
        service = get_object_or_404(Service, pk=service_id)
        audit_source = get_object_or_404(AuditSource, pk=audit_source_id)
        
        # Récupérer le validateur assigné pour ce niveau (s'il existe)
        validateur_assigne = ValidateurService.get_validateurs_service(
            service, audit_source=audit_source, niveau=niveau
        ).first()
        
        context = {
            'service': service,
            'audit_source': audit_source,
            'niveau': niveau,
            'validateur_assigne': validateur_assigne,
        }
        
        return render(request, 'core/workflow/niveau_partial.html', context)
        
    except Exception as e:
        from django.http import HttpResponse
        return HttpResponse(f'<div class="text-red-500">Erreur: {str(e)}</div>', status=500)