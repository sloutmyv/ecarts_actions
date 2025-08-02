"""
Vues pour la gestion des écarts et des déclarations.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime

from core.models import GapReport, Gap, AuditSource, Service, Process, GapType, User
from core.forms import GapReportForm, GapForm


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
    
    # Récupérer tous les services pour le filtre
    services = Service.objects.all().order_by('nom')
    
    context = {
        'gaps': gaps,
        'services': services,
        'selected_service': selected_service,
        'page_title': 'Gestion des Écarts'
    }
    return render(request, 'core/gaps/gap_list.html', context)


@login_required
def gap_report_list(request):
    """
    Liste des déclarations d'écart.
    """
    gap_reports = GapReport.objects.select_related(
        'audit_source', 'service', 'process', 'declared_by'
    ).prefetch_related('gaps').order_by('-observation_date', '-created_at')
    
    context = {
        'gap_reports': gap_reports,
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
    
    context = {
        'gap_report': gap_report,
        'title': f'Déclaration {gap_report.id}'
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
            gap_report = GapReport(
                audit_source_id=request.POST.get('audit_source'),
                source_reference=request.POST.get('source_reference', ''),
                service_id=request.POST.get('service'),
                location=request.POST.get('location', ''),
                observation_date=request.POST.get('observation_date'),
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
            
            messages.success(request, f'Déclaration d\'écart {gap_report.id} créée avec succès.')
            
            if request.headers.get('HX-Request'):
                from django.http import HttpResponse
                from django.urls import reverse
                response = HttpResponse()
                response['HX-Redirect'] = reverse('gaps:gap_list')
                return response
            return redirect('gaps:gap_report_detail', pk=gap_report.pk)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            if request.headers.get('HX-Request'):
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': f'Erreur: {str(e)}'
                })
    
    # GET request - afficher le formulaire
    services = Service.objects.all().order_by('nom')
    audit_sources = AuditSource.objects.filter(is_active=True)
    processes = Process.objects.filter(is_active=True)
    users = User.objects.all().order_by('nom', 'prenom')
    
    context = {
        'services': services,
        'audit_sources': audit_sources,
        'processes': processes,
        'users': users,
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
    """
    gap_report = get_object_or_404(GapReport, pk=pk)
    
    if request.method == 'POST':
        form = GapReportForm(request.POST, instance=gap_report, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Déclaration d\'écart {gap_report.id} modifiée avec succès.')
            return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    else:
        form = GapReportForm(instance=gap_report, user=request.user)
    
    context = {
        'form': form,
        'gap_report': gap_report,
        'title': f'Modifier la déclaration {gap_report.id}',
        'submit_text': 'Sauvegarder les modifications'
    }
    return render(request, 'core/gaps/gap_report_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def gap_create(request, gap_report_pk):
    """
    Création d'un nouvel écart pour une déclaration existante.
    """
    gap_report = get_object_or_404(GapReport, pk=gap_report_pk)
    
    if request.method == 'POST':
        form = GapForm(request.POST, gap_report=gap_report)
        if form.is_valid():
            gap = form.save(commit=False)
            gap.gap_report = gap_report
            gap.save()
            
            messages.success(request, f'Écart {gap.gap_number} créé avec succès.')
            return redirect('gaps:gap_report_detail', pk=gap_report.pk)
    else:
        form = GapForm(gap_report=gap_report)
    
    context = {
        'form': form,
        'gap_report': gap_report,
        'title': f'Nouvel écart pour la déclaration {gap_report.id}',
        'submit_text': 'Créer l\'écart'
    }
    return render(request, 'core/gaps/gap_form.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def gap_edit(request, pk):
    """
    Modification d'un écart existant.
    """
    gap = get_object_or_404(Gap.objects.select_related('gap_report'), pk=pk)
    
    if request.method == 'POST':
        form = GapForm(request.POST, instance=gap, gap_report=gap.gap_report)
        if form.is_valid():
            form.save()
            messages.success(request, f'Écart {gap.gap_number} modifié avec succès.')
            return redirect('gaps:gap_report_detail', pk=gap.gap_report.pk)
    else:
        form = GapForm(instance=gap, gap_report=gap.gap_report)
    
    context = {
        'form': form,
        'gap': gap,
        'gap_report': gap.gap_report,
        'title': f'Modifier l\'écart {gap.gap_number}',
        'submit_text': 'Sauvegarder les modifications'
    }
    return render(request, 'core/gaps/gap_form.html', context)


@login_required
def get_gap_types(request):
    """
    API HTMX pour récupérer les types d'écart selon la source d'audit sélectionnée.
    """
    audit_source_id = request.GET.get('audit_source_id')
    
    if audit_source_id:
        gap_types = GapType.objects.filter(
            audit_source_id=audit_source_id,
            is_active=True
        ).order_by('name')
    else:
        gap_types = GapType.objects.none()
    
    context = {
        'gap_types': gap_types,
        'selected_gap_type': request.GET.get('selected_gap_type')
    }
    return render(request, 'core/gaps/partials/gap_type_options.html', context)


@login_required
def get_process_field(request):
    """
    API HTMX pour afficher/masquer le champ processus selon la source d'audit.
    """
    audit_source_id = request.GET.get('audit_source_id')
    
    if audit_source_id:
        try:
            audit_source = AuditSource.objects.get(id=audit_source_id)
            requires_process = audit_source.requires_process
        except AuditSource.DoesNotExist:
            requires_process = False
    else:
        requires_process = False
    
    if requires_process:
        processes = Process.objects.filter(is_active=True).order_by('name')
    else:
        processes = Process.objects.none()
    
    context = {
        'requires_process': requires_process,
        'processes': processes,
        'selected_process': request.GET.get('selected_process')
    }
    return render(request, 'core/gaps/partials/process_field.html', context)