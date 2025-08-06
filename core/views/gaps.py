"""
Vues pour la gestion des écarts et des déclarations.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime

from core.models import GapReport, Gap, AuditSource, Service, Process, GapType, User, GapReportAttachment, GapAttachment, HistoriqueModification
from core.forms import GapReportForm, GapForm, GapAttachmentForm


def get_services_hierarchical_order():
    """Retourne les services triés par ordre alphabétique hiérarchique."""
    services_ordered = []
    
    # D'abord, récupérer tous les services racines triés par nom
    services_racines = Service.objects.filter(parent__isnull=True).order_by('nom')
    
    def add_service_and_children(service, level=0):
        """Ajoute récursivement un service et ses enfants triés par nom."""
        services_ordered.append(service)
        # Récupérer les sous-services triés par nom
        sous_services = service.sous_services.order_by('nom')
        for sous_service in sous_services:
            add_service_and_children(sous_service, level + 1)
    
    # Construire la liste hiérarchique
    for service_racine in services_racines:
        add_service_and_children(service_racine)
    
    return services_ordered


@login_required
def gap_list(request):
    """
    Liste de tous les écarts individuels.
    """
    # Filtrage par service si fourni
    selected_service = request.GET.get('service')
    gaps = Gap.objects.select_related(
        'gap_report__audit_source', 'gap_report__service', 'gap_report__declared_by', 'gap_type'
    ).order_by('-created_at')
    
    if selected_service:
        gaps = gaps.filter(gap_report__service_id=selected_service)
    
    # Filtrer les écarts selon la visibilité pour l'utilisateur connecté
    visible_gaps = []
    for gap in gaps:
        if gap.is_visible_to_user(request.user):
            visible_gaps.append(gap)
    
    # Récupérer tous les services pour le filtre
    services = get_services_hierarchical_order()
    
    context = {
        'gaps': visible_gaps,
        'services': services,
        'selected_service': selected_service,
        'page_title': 'Liste des Écarts'
    }
    return render(request, 'core/gaps/gap_list.html', context)


@login_required
def gap_report_list(request):
    """
    Liste des Déclarations d'évenements avec filtres.
    Par défaut, filtre selon les informations de l'utilisateur connecté.
    """
    # Récupérer les paramètres de filtrage
    selected_service = request.GET.get('service')
    declared_by_search = request.GET.get('declared_by_search', '').strip()
    selected_audit_source = request.GET.get('audit_source')
    show_all = request.GET.get('show_all', False)  # Paramètre pour afficher tout
    
    # Base queryset
    gap_reports = GapReport.objects.select_related(
        'audit_source', 'service', 'process', 'declared_by'
    ).prefetch_related('gaps')
    
    # Vérifier si l'utilisateur a soumis le formulaire de filtrage
    form_submitted = 'service' in request.GET or 'declared_by_search' in request.GET or 'audit_source' in request.GET
    
    # Vérifier si des filtres explicites sont appliqués via GET
    has_explicit_filters = form_submitted or show_all
    
    # Filtrage par défaut selon l'utilisateur connecté (si aucun filtre explicite n'est appliqué)
    if not has_explicit_filters:
        # Par défaut, créer un filtre combiné pour l'utilisateur connecté :
        # 1. Écarts de son service (si il en a un)
        # 2. Écarts qu'il a déclarés
        # 3. Écarts auxquels il est impliqué (involved_users)
        
        user_filter = Q(declared_by=request.user)  # Écarts qu'il a déclarés
        user_filter |= Q(involved_users=request.user)  # Écarts auxquels il est impliqué
        
        # Si l'utilisateur a un service, inclure aussi les écarts de ce service
        if request.user.service:
            user_filter |= Q(service=request.user.service)
            selected_service = str(request.user.service.id)  # Pré-sélectionner le service dans le filtre
        
        gap_reports = gap_reports.filter(user_filter)
    elif show_all:
        # Afficher toutes les déclarations sans aucun filtre
        pass  # gap_reports reste non filtré
    else:
        # Appliquer les filtres sélectionnés explicitement
        if selected_service:
            gap_reports = gap_reports.filter(service_id=selected_service)
        # Si selected_service est une chaîne vide (""), cela signifie "Toutes les entités"
        # Dans ce cas, on ne filtre pas par service (on garde tous les services)
        
        if declared_by_search:
            # Si c'est un ID utilisateur (sélectionné via autocomplétion)
            declared_by_id = request.GET.get('declared_by_id')
            if declared_by_id:
                gap_reports = gap_reports.filter(declared_by_id=declared_by_id)
            else:
                # Recherche textuelle dans nom, prénom ou matricule
                search_terms = declared_by_search.split()
                
                # Si plusieurs mots, chercher les combinaisons nom+prénom
                if len(search_terms) > 1:
                    # Recherche "prénom nom" ou "nom prénom"
                    gap_reports = gap_reports.filter(
                        Q(declared_by__nom__icontains=search_terms[0], declared_by__prenom__icontains=search_terms[1]) |
                        Q(declared_by__nom__icontains=search_terms[1], declared_by__prenom__icontains=search_terms[0]) |
                        Q(declared_by__matricule__icontains=declared_by_search)
                    )
                else:
                    # Recherche simple dans un seul champ
                    gap_reports = gap_reports.filter(
                        Q(declared_by__nom__icontains=declared_by_search) |
                        Q(declared_by__prenom__icontains=declared_by_search) |
                        Q(declared_by__matricule__icontains=declared_by_search)
                    )
        
        if selected_audit_source:
            gap_reports = gap_reports.filter(audit_source_id=selected_audit_source)
    
    # Supprimer les doublons et ordonner
    gap_reports = gap_reports.distinct().order_by('-observation_date', '-created_at')
    
    # Récupérer les données pour les filtres
    services = get_services_hierarchical_order()
    audit_sources = AuditSource.objects.all().order_by('name')
    
    # Récupérer le nom du service sélectionné pour l'affichage
    selected_service_name = None
    if selected_service:
        try:
            from core.models import Service
            service_obj = Service.objects.get(id=selected_service)
            selected_service_name = service_obj.nom
        except (Service.DoesNotExist, ValueError):
            pass
    
    context = {
        'gap_reports': gap_reports,
        'services': services,
        'audit_sources': audit_sources,
        'selected_service': selected_service,
        'selected_service_name': selected_service_name,
        'declared_by_search': declared_by_search,
        'declared_by_id': request.GET.get('declared_by_id', ''),
        'selected_audit_source': selected_audit_source,
        'show_all': show_all,
        'form_submitted': form_submitted,
        'title': 'Déclarations d\'écart'
    }
    return render(request, 'core/gaps/gap_report_list.html', context)


@login_required
def gap_report_detail(request, pk):
    """
    Détail d'une déclaration d'écart avec ses écarts associés.
    """
    gap_report = get_object_or_404(
        GapReport.objects.select_related(
            'audit_source', 'service', 'process', 'declared_by'
        ).prefetch_related('gaps__gap_type', 'involved_users'),
        pk=pk
    )
    
    # Filtrer les écarts selon la visibilité pour l'utilisateur connecté
    visible_gaps = []
    for gap in gap_report.gaps.all():
        if gap.is_visible_to_user(request.user):
            visible_gaps.append(gap)
    
    # Récupérer l'historique complet de la déclaration (pour admin/superadmin uniquement)
    historique = []
    if request.user.droits in ['SA', 'AD']:
        historique = HistoriqueModification.objects.filter(
            gap_report=gap_report
        ).select_related('utilisateur').order_by('-created_at')[:50]  # Limiter à 50 entrées récentes
    
    context = {
        'gap_report': gap_report,
        'visible_gaps': visible_gaps,
        'historique': historique,
        'title': f'Détail de la déclaration #{gap_report.id}'
    }
    return render(request, 'core/gaps/gap_report_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def gap_report_create(request):
    """
    Création d'une nouvelle déclaration d'écart.
    Supporte les requêtes HTMX pour affichage en modal.
    """
    if request.method == 'POST':
        try:
            from django.db import transaction
            
            with transaction.atomic():
                # Créer la déclaration d'écart (entête)
                gap_report = GapReport(
                    audit_source_id=request.POST.get('audit_source'),
                    source_reference=request.POST.get('source_reference', ''),
                    service_id=request.POST.get('service'),
                    location=request.POST.get('location', ''),
                    observation_date=request.POST.get('observation_datetime'),
                    declared_by=request.user
                )
                
                process_id = request.POST.get('process')
                if process_id:
                    gap_report.process_id = process_id
                
                gap_report.full_clean()
                gap_report.save()
                
                # Gérer les utilisateurs impliqués
                involved_users_str = request.POST.get('involved_users', '')
                if involved_users_str.strip():
                    try:
                        involved_users_ids = [int(id.strip()) for id in involved_users_str.split(',') if id.strip().isdigit()]
                        if involved_users_ids:
                            gap_report.involved_users.set(involved_users_ids)
                    except (ValueError, TypeError):
                        # Ignorer si les IDs ne sont pas valides
                        pass
                
                # Traiter les pièces jointes de la déclaration
                for key in request.POST.keys():
                    if key.startswith('declaration_attachment_name_'):
                        index = key.split('_')[-1]
                        attachment_name = request.POST.get(f'declaration_attachment_name_{index}')
                        attachment_file = request.FILES.get(f'declaration_attachment_file_{index}')
                        
                        if attachment_name and attachment_file:
                            attachment = GapReportAttachment(
                                gap_report=gap_report,
                                name=attachment_name,
                                file=attachment_file,
                                uploaded_by=request.user
                            )
                            attachment.full_clean()
                            attachment.save()
                
                # Créer les écarts individuels
                gap_count = 0
                gaps_created = []
                
                # Parcourir tous les champs POST pour trouver les écarts
                for key in request.POST.keys():
                    if key.startswith('gap_type_'):
                        index = key.split('_')[-1]
                        gap_type_id = request.POST.get(f'gap_type_{index}')
                        gap_description = request.POST.get(f'gap_description_{index}')
                        
                        if gap_type_id and gap_description:
                            gap = Gap(
                                gap_report=gap_report,
                                gap_type_id=gap_type_id,
                                description=gap_description
                            )
                            # Le gap_number sera généré automatiquement dans save()
                            gap.save()
                            gaps_created.append(gap)
                            gap_count += 1
                            
                            # Traiter les pièces jointes de cet écart
                            for file_key in request.POST.keys():
                                if file_key.startswith(f'gap_{index}_attachment_name_'):
                                    attachment_index = file_key.split('_')[-1]
                                    attachment_name = request.POST.get(f'gap_{index}_attachment_name_{attachment_index}')
                                    attachment_file = request.FILES.get(f'gap_{index}_attachment_file_{attachment_index}')
                                    
                                    if attachment_name and attachment_file:
                                        gap_attachment = GapAttachment(
                                            gap=gap,
                                            name=attachment_name,
                                            file=attachment_file,
                                            uploaded_by=request.user
                                        )
                                        gap_attachment.full_clean()
                                        gap_attachment.save()
            
            if gap_count == 1:
                messages.success(request, f'Écart {gaps_created[0].gap_number} créé avec succès.')
            else:
                gap_numbers = [gap.gap_number for gap in gaps_created]
                messages.success(request, f'{gap_count} écarts créés avec succès : {", ".join(gap_numbers)}')
            
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                from django.urls import reverse
                response = HttpResponse()
                response['HX-Redirect'] = reverse('gaps:gap_list')
                return response
            return redirect('gaps:gap_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            if request.headers.get('HX-Request'):
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': f'Erreur: {str(e)}'
                })
    
    # GET request - afficher le formulaire
    services = get_services_hierarchical_order()
    audit_sources = AuditSource.objects.all().order_by('name')
    processes = Process.objects.filter(is_active=True).order_by('code')
    users = User.objects.all().order_by('nom', 'prenom')
    gap_types = GapType.objects.all().order_by('audit_source__name', 'name')
    
    context = {
        'services': services,
        'audit_sources': audit_sources,
        'processes': processes,
        'users': users,
        'gap_types': gap_types,
        'user': request.user,
        'csrf_token': request.META.get('CSRF_COOKIE')
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'core/gaps/gap_report_form_modal.html', context)
    else:
        form = GapReportForm(
            initial={'observation_date': datetime.now().date()},
            user=request.user
        )
        context.update({
            'form': form,
            'title': 'Nouvelle déclaration d\'écart',
            'submit_text': 'Créer la déclaration'
        })
        return render(request, 'core/gaps/gap_report_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def gap_report_edit(request, pk):
    """
    Modification d'une déclaration d'écart existante.
    Seul le déclarant peut modifier une déclaration.
    """
    gap_report = get_object_or_404(GapReport, pk=pk)
    
    # Vérifier que l'utilisateur connecté est le déclarant ou un administrateur
    if gap_report.declared_by != request.user and request.user.droits not in ['SA', 'AD']:
        messages.error(request, 'Vous ne pouvez modifier que vos propres déclarations.')
        return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    
    if request.method == 'POST':
        form = GapReportForm(request.POST, request.FILES, instance=gap_report, user=request.user)
        if form.is_valid():
            gap_report = form.save()
            
            # Gérer les utilisateurs impliqués depuis le champ caché
            involved_users_str = request.POST.get('involved_users', '')
            if involved_users_str.strip():
                try:
                    involved_users_ids = [int(id.strip()) for id in involved_users_str.split(',') if id.strip().isdigit()]
                    gap_report.involved_users.set(involved_users_ids)
                except (ValueError, TypeError):
                    pass
            else:
                gap_report.involved_users.clear()
            
            # Traiter les nouvelles pièces jointes
            for key in request.POST.keys():
                if key.startswith('attachment_name_'):
                    index = key.split('_')[-1]
                    attachment_name = request.POST.get(f'attachment_name_{index}')
                    attachment_file = request.FILES.get(f'attachment_file_{index}')
                    
                    if attachment_name and attachment_file:
                        from core.models import GapReportAttachment
                        attachment = GapReportAttachment(
                            gap_report=gap_report,
                            name=attachment_name,
                            file=attachment_file,
                            uploaded_by=request.user
                        )
                        attachment.full_clean()
                        attachment.save()
            
            messages.success(request, f'Déclaration d\'écart #{gap_report.id} modifiée avec succès.')
            return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    else:
        form = GapReportForm(instance=gap_report, user=request.user)
    
    context = {
        'form': form,
        'gap_report': gap_report,
        'title': f'Modification de la déclaration #{gap_report.id}',
        'submit_text': 'Sauvegarder les modifications'
    }
    return render(request, 'core/gaps/gap_report_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def gap_create(request, gap_report_pk):
    """
    Création d'un nouvel écart pour une déclaration existante.
    Seul le déclarant peut ajouter des écarts à sa déclaration.
    """
    gap_report = get_object_or_404(GapReport, pk=gap_report_pk)
    
    # Vérifier que l'utilisateur connecté est le déclarant ou un administrateur
    if gap_report.declared_by != request.user and request.user.droits not in ['SA', 'AD']:
        messages.error(request, 'Vous ne pouvez ajouter des écarts qu\'à vos propres déclarations.')
        return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    
    if request.method == 'POST':
        form = GapForm(request.POST, gap_report=gap_report, user=request.user)
        if form.is_valid():
            gap = form.save(commit=False)
            gap.gap_report = gap_report
            # Le gap_number sera généré automatiquement dans la méthode save() du modèle
            gap.save()
            
            messages.success(request, f'Écart {gap.gap_number} créé avec succès.')
            return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    else:
        form = GapForm(gap_report=gap_report, user=request.user)
    
    context = {
        'form': form,
        'gap_report': gap_report,
        'title': f'Nouvel écart pour la déclaration #{gap_report.id}',
        'submit_text': 'Créer l\'écart'
    }
    return render(request, 'core/gaps/gap_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def gap_edit(request, pk):
    """
    Modification d'un écart existant.
    Seul le déclarant de la déclaration peut modifier ses écarts.
    """
    gap = get_object_or_404(Gap.objects.select_related('gap_report'), pk=pk)
    
    # Vérifier que l'utilisateur connecté est le déclarant de la déclaration ou un administrateur
    if gap.gap_report.declared_by != request.user and request.user.droits not in ['SA', 'AD']:
        messages.error(request, 'Vous ne pouvez modifier que les écarts de vos propres déclarations.')
        return redirect('gaps:gap_report_detail', pk=gap.gap_report.pk)
    
    if request.method == 'POST':
        form = GapForm(request.POST, instance=gap, gap_report=gap.gap_report, user=request.user)
        if form.is_valid():
            form.save()
            
            # Gérer l'ajout de pièces jointes multiples
            attachment_names = request.POST.getlist('attachment_name')
            attachment_files = request.FILES.getlist('attachment_file')
            
            # Traiter chaque pièce jointe
            for i, (name, file) in enumerate(zip(attachment_names, attachment_files)):
                if name and file:  # S'assurer que les deux champs sont fournis
                    try:
                        attachment = GapAttachment(
                            gap=gap,
                            name=name,
                            file=file,
                            uploaded_by=request.user
                        )
                        attachment.full_clean()  # Validation
                        attachment.save()
                        messages.success(request, f'Pièce jointe "{name}" ajoutée avec succès.')
                    except Exception as e:
                        messages.error(request, f'Erreur lors de l\'ajout de la pièce jointe "{name}" : {str(e)}')
            
            messages.success(request, f'Écart {gap.gap_number} modifié avec succès.')
            return redirect('gaps:gap_report_detail', pk=gap.gap_report.pk)
    else:
        form = GapForm(instance=gap, gap_report=gap.gap_report, user=request.user)
    
    context = {
        'form': form,
        'gap': gap,
        'gap_report': gap.gap_report,
        'title': f'Modifier l\'écart {gap.gap_number}',
        'submit_text': 'Sauvegarder les modifications'
    }
    return render(request, 'core/gaps/gap_form.html', context)


@login_required
@require_http_methods(["POST"])
def delete_gap_attachment(request, pk):
    """
    Supprime une pièce jointe d'écart.
    Seuls le déclarant de la déclaration ou un administrateur peuvent supprimer des pièces jointes.
    """
    attachment = get_object_or_404(GapAttachment.objects.select_related('gap__gap_report'), pk=pk)
    gap_report = attachment.gap.gap_report
    
    # Vérifier que l'utilisateur connecté est le déclarant de la déclaration ou un administrateur
    if gap_report.declared_by != request.user and request.user.droits not in ['SA', 'AD']:
        messages.error(request, 'Vous ne pouvez supprimer que les pièces jointes de vos propres déclarations.')
        return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    
    # Sauvegarder le nom et l'écart pour le message
    attachment_name = attachment.name
    gap = attachment.gap
    
    # Supprimer le fichier physique
    if attachment.file:
        try:
            attachment.file.delete(save=False)
        except Exception:
            pass  # Ignorer les erreurs de suppression de fichier
    
    # Supprimer l'enregistrement
    attachment.delete()
    
    messages.success(request, f'Pièce jointe "{attachment_name}" supprimée avec succès.')
    return redirect('gaps:gap_edit', pk=gap.pk)


@login_required
@require_http_methods(["POST"])
def delete_gap(request, pk):
    """
    Affiche la popup de confirmation pour supprimer un écart.
    Seuls les Super Administrateurs (SA) et Administrateurs (AD) peuvent supprimer des écarts.
    """
    gap = get_object_or_404(Gap.objects.select_related('gap_report'), pk=pk)
    gap_report = gap.gap_report
    
    # Vérifier que l'utilisateur connecté est un administrateur
    if request.user.droits not in ['SA', 'AD']:
        messages.error(request, 'Vous n\'avez pas les droits nécessaires pour supprimer un écart.')
        return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    
    # Vérifier si c'est le dernier écart de la déclaration
    total_gaps = gap_report.gaps.count()
    is_last_gap = total_gaps == 1
    
    # Préparer le message de confirmation
    attachment_count = gap.attachments.count()
    
    if is_last_gap:
        # Message spécial pour le dernier écart
        if attachment_count > 0:
            message = f'⚠️ ATTENTION : Vous êtes sur le point de supprimer le dernier écart de cette déclaration.\n\nCette action supprimera :\n• L\'écart "{gap.gap_number}"\n• Ses {attachment_count} pièce(s) jointe(s)\n• La déclaration d\'écart #{gap_report.id} dans son intégralité\n\nCette action est IRRÉVERSIBLE et effacera complètement la déclaration.'
        else:
            message = f'⚠️ ATTENTION : Vous êtes sur le point de supprimer le dernier écart de cette déclaration.\n\nCette action supprimera :\n• L\'écart "{gap.gap_number}"\n• La déclaration d\'écart #{gap_report.id} dans son intégralité\n\nCette action est IRRÉVERSIBLE et effacera complètement la déclaration.'
    else:
        # Message normal pour un écart parmi d'autres
        if attachment_count > 0:
            message = f'Êtes-vous sûr de vouloir supprimer définitivement l\'écart "{gap.gap_number}" ?\n\nCette action supprimera également {attachment_count} pièce(s) jointe(s) associée(s) et est irréversible.'
        else:
            message = f'Êtes-vous sûr de vouloir supprimer définitivement l\'écart "{gap.gap_number}" ?\n\nCette action est irréversible.'
    
    # Si c'est une requête HTMX, retourner la popup de confirmation
    if request.headers.get('HX-Request'):
        from django.template.loader import render_to_string
        from django.middleware.csrf import get_token
        
        notification_html = render_to_string('core/gaps/notification_confirm.html', {
            'message': message,
            'gap': gap,
            'csrf_token': get_token(request)
        })
        
        from django.http import HttpResponse
        response = HttpResponse(notification_html)
        response['HX-Retarget'] = '#modal-container'
        response['HX-Reswap'] = 'innerHTML'
        return response
    
    # Si ce n'est pas HTMX, rediriger vers la page de détail
    return redirect('gaps:gap_report_detail', pk=gap_report.pk)


@login_required
@require_http_methods(["POST"])
def delete_gap_confirm(request, pk):
    """
    Suppression définitive d'un écart après confirmation.
    Seuls les Super Administrateurs (SA) et Administrateurs (AD) peuvent supprimer des écarts.
    """
    gap = get_object_or_404(Gap.objects.select_related('gap_report'), pk=pk)
    gap_report = gap.gap_report
    
    # Vérifier que l'utilisateur connecté est un administrateur
    if request.user.droits not in ['SA', 'AD']:
        messages.error(request, 'Vous n\'avez pas les droits nécessaires pour supprimer un écart.')
        return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    
    # Vérifier si c'est le dernier écart de la déclaration
    total_gaps = gap_report.gaps.count()
    is_last_gap = total_gaps == 1
    
    # Sauvegarder les informations pour le message
    gap_number = gap.gap_number
    gap_report_id = gap_report.id
    
    # Supprimer les pièces jointes de l'écart
    for attachment in gap.attachments.all():
        if attachment.file:
            try:
                attachment.file.delete(save=False)
            except Exception:
                pass  # Ignorer les erreurs de suppression de fichier
        attachment.delete()
    
    # Supprimer l'écart
    gap.delete()
    
    if is_last_gap:
        # Si c'était le dernier écart, supprimer aussi la déclaration
        
        # Supprimer les pièces jointes de la déclaration
        for attachment in gap_report.attachments.all():
            if attachment.file:
                try:
                    attachment.file.delete(save=False)
                except Exception:
                    pass
            attachment.delete()
        
        # Supprimer la déclaration
        gap_report.delete()
        
        # Message de succès pour suppression complète
        messages.success(request, f'Écart "{gap_number}" et déclaration #{gap_report_id} supprimés définitivement avec succès.')
        
        # Rediriger vers la liste des déclarations
        if request.headers.get('HX-Request'):
            from django.http import HttpResponse
            response = HttpResponse('')
            response['HX-Trigger'] = 'gapReportDeleted'
            response['HX-Redirect'] = '/gaps/declarations/'
            return response
        
        return redirect('gaps:gap_report_list')
    else:
        # Supprimer seulement l'écart
        messages.success(request, f'Écart "{gap_number}" supprimé définitivement avec succès.')
        
        # Rediriger vers la déclaration
        if request.headers.get('HX-Request'):
            from django.http import HttpResponse
            response = HttpResponse('')
            response['HX-Trigger'] = 'gapDeleted'
            response['HX-Redirect'] = f'/gaps/declaration/{gap_report.pk}/'
            return response
        
        return redirect('gaps:gap_report_detail', pk=gap_report.pk)


@login_required
def get_gap_types(request):
    """
    API HTMX pour récupérer les types d'écart selon la source d'audit sélectionnée.
    """
    audit_source_id = request.GET.get('audit_source_id')
    
    if audit_source_id:
        gap_types = GapType.objects.filter(
            audit_source_id=audit_source_id
        ).order_by('name')
    else:
        gap_types = GapType.objects.none()
    
    # Retourner directement les options HTML
    options_html = '<option value="">Sélectionner un type d\'écart</option>'
    for gap_type in gap_types:
        selected = 'selected' if str(gap_type.id) == request.GET.get('selected_gap_type') else ''
        options_html += f'<option value="{gap_type.id}" {selected}>{gap_type.name}</option>'
    
    from django.http import HttpResponse
    return HttpResponse(options_html)


@login_required
def get_process_field(request):
    """
    API HTMX pour afficher/masquer le champ processus selon la source d'audit.
    """
    audit_source_id = request.GET.get('audit_source')
    
    if audit_source_id:
        try:
            audit_source = AuditSource.objects.get(id=audit_source_id)
            requires_process = audit_source.requires_process
        except AuditSource.DoesNotExist:
            requires_process = False
    else:
        requires_process = False
    
    if requires_process:
        processes = Process.objects.filter(is_active=True).order_by('code')
    else:
        processes = Process.objects.none()
    
    context = {
        'requires_process': requires_process,
        'processes': processes,
        'selected_process': request.GET.get('selected_process')
    }
    return render(request, 'core/gaps/partials/process_field.html', context)


@login_required
def search_users(request):
    """
    API AJAX pour la recherche d'utilisateurs (autocomplétion).
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 1:
        return JsonResponse({'users': []})
    
    # Si la requête est "all", retourner tous les utilisateurs (pour l'initialisation)
    if query.lower() == 'all':
        users = User.objects.all().order_by('nom', 'prenom')[:100]  # Limiter à 100 utilisateurs
    else:
        # Rechercher dans nom, prénom ou matricule
        users = User.objects.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(matricule__icontains=query)
        ).order_by('nom', 'prenom')[:10]  # Limiter à 10 résultats
    
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'name': user.get_full_name() or user.matricule,
            'matricule': user.matricule,
        })
    
    return JsonResponse({'users': users_data})


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_attachment(request, attachment_id):
    """
    Supprime une pièce jointe de déclaration.
    """
    from core.models import GapReportAttachment
    from django.http import JsonResponse
    import os
    
    try:
        attachment = get_object_or_404(GapReportAttachment, id=attachment_id)
        
        # Vérifier que l'utilisateur a le droit de supprimer cette pièce jointe
        # (déclarant, uploader du fichier, ou administrateur)
        if (attachment.gap_report.declared_by != request.user and 
            attachment.uploaded_by != request.user and 
            request.user.droits not in ['SA', 'AD']):
            return JsonResponse({
                'success': False,
                'error': 'Vous n\'avez pas l\'autorisation de supprimer cette pièce jointe.'
            }, status=403)
        
        # Supprimer le fichier physique
        if attachment.file and os.path.exists(attachment.file.path):
            os.remove(attachment.file.path)
        
        # Supprimer l'enregistrement en base de données
        attachment.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Pièce jointe supprimée avec succès.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la suppression : {str(e)}'
        }, status=500)