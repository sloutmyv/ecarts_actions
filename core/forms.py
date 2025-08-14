"""
Formulaires pour la gestion des écarts.
"""
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

from core.models import GapReport, Gap, AuditSource, Service, Process, GapType, GapAttachment


class GapReportForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une déclaration d'écart.
    """
    
    class Meta:
        model = GapReport
        fields = [
            'audit_source', 'source_reference', 'service', 'process',
            'location', 'observation_date'
        ]
        widgets = {
            'audit_source': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'hx-get': '/gaps/api/process-field/',
                'hx-target': '#process-field',
                'hx-include': '[name="audit_source"]'
            }),
            'source_reference': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'placeholder': 'Référence optionnelle'
            }),
            'service': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'hx-get': '/gaps/api/audit-sources-field/',
                'hx-target': '#audit-source-field',
                'hx-include': '[name="service"]'
            }),
            'process': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors'}),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'placeholder': 'Lieu de l\'observation'
            }),
            'observation_date': forms.DateTimeInput(
                attrs={
                    'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            )
        }
        labels = {
            'audit_source': 'Source de l\'audit',
            'source_reference': 'Référence source',
            'service': 'Service concerné',
            'process': 'Processus SMI associé',
            'location': 'Lieu',
            'observation_date': 'Date d\'observation'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Récupérer l'utilisateur connecté
        super().__init__(*args, **kwargs)
        
        # Configurer le format datetime-local pour le champ observation_date
        self.fields['observation_date'].input_formats = ['%Y-%m-%dT%H:%M']
        
        # Définir les choix disponibles pour les sources d'audit selon le service
        # Si un service est fourni dans les données initiales ou instance, filtrer les sources
        service = None
        if self.instance.pk and hasattr(self.instance, 'service') and self.instance.service:
            service = self.instance.service
        elif 'service' in self.initial:
            try:
                service = Service.objects.get(id=self.initial['service'])
            except (Service.DoesNotExist, ValueError, TypeError):
                pass
        elif self.user and self.user.service:
            # Utiliser le service de l'utilisateur par défaut
            service = self.user.service
            
        if service:
            # Filtrer les sources d'audit qui ont des validateurs pour ce service
            from .models.workflow import ValidateurService
            sources_with_validators = ValidateurService.objects.filter(
                service=service,
                actif=True,
                audit_source__is_active=True
            ).values_list('audit_source', flat=True).distinct()
            
            self.fields['audit_source'].queryset = AuditSource.objects.filter(
                id__in=sources_with_validators,
                is_active=True
            ).order_by('name')
        else:
            # Aucun service défini, afficher toutes les sources actives
            self.fields['audit_source'].queryset = AuditSource.objects.filter(is_active=True).order_by('name')
        
        # Utiliser le tri hiérarchique pour les services
        from core.views.gaps import get_services_hierarchical_order
        services_ordered = get_services_hierarchical_order()
        self.fields['service'].queryset = Service.objects.filter(
            id__in=[s.id for s in services_ordered]
        ).order_by('nom')
        # Réorganiser selon l'ordre hiérarchique
        service_choices = [(s.id, s.get_chemin_hierarchique()) for s in services_ordered]
        self.fields['service'].choices = [('', '---------')] + service_choices
        
        self.fields['process'].queryset = Process.objects.filter(is_active=True)
        
        # Définir la date par défaut uniquement pour les nouvelles créations
        if not self.instance.pk and 'observation_date' not in self.initial:
            self.fields['observation_date'].initial = datetime.now().strftime('%Y-%m-%dT%H:%M')
        # Pour les modifications, Django gère automatiquement la valeur depuis l'instance
        
        # Pré-sélectionner le service de l'utilisateur connecté
        if not self.instance.pk and self.user and self.user.service and 'service' not in self.initial:
            self.fields['service'].initial = self.user.service
        
        # Rendre le champ processus optionnel par défaut
        self.fields['process'].required = False
        
        # Désactiver le champ audit_source si des écarts existent déjà
        if self.instance.pk and self.instance.gaps.exists():
            self.fields['audit_source'].disabled = True
            self.fields['audit_source'].help_text = "La source d'audit ne peut pas être modifiée car des écarts sont déjà associés à cette déclaration."

    def clean(self):
        cleaned_data = super().clean()
        audit_source = cleaned_data.get('audit_source')
        process = cleaned_data.get('process')
        observation_date = cleaned_data.get('observation_date')
        
        # Vérifier que la date d'observation n'est pas postérieure à la date de déclaration
        if observation_date:
            from django.utils import timezone
            current_time = timezone.now()
            
            # Pour une modification, utiliser la date de création comme référence
            if self.instance.pk:
                declaration_date = self.instance.created_at
            else:
                declaration_date = current_time
            
            # S'assurer que observation_date est timezone-aware pour la comparaison
            if timezone.is_naive(observation_date):
                observation_date = timezone.make_aware(observation_date)
            
            if observation_date > declaration_date:
                raise ValidationError({
                    'observation_date': 'La date d\'observation ne peut pas être postérieure à la date de déclaration.'
                })
        
        # Vérifier que la source d'audit n'est pas modifiée si des écarts existent
        if self.instance.pk and self.instance.gaps.exists():
            original_audit_source = self.instance.audit_source
            if audit_source and audit_source != original_audit_source:
                raise ValidationError({
                    'audit_source': 'La source d\'audit ne peut pas être modifiée car des écarts sont déjà associés à cette déclaration.'
                })
        
        if audit_source:
            if audit_source.requires_process and not process:
                raise ValidationError({
                    'process': 'Un processus est obligatoire pour cette source d\'audit.'
                })
            elif not audit_source.requires_process and process:
                raise ValidationError({
                    'process': 'Aucun processus ne doit être sélectionné pour cette source d\'audit.'
                })
        
        return cleaned_data


class GapForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier un écart.
    """
    
    class Meta:
        model = Gap
        fields = ['gap_type', 'description', 'status']
        widgets = {
            'gap_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'rows': 4,
                'placeholder': 'Décrivez l\'écart et ses causes...'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors'
            })
        }
        labels = {
            'gap_type': 'Type d\'écart (Quoi) *',
            'description': 'Description (Pourquoi) *',
            'status': 'Statut *'
        }

    def __init__(self, *args, **kwargs):
        self.gap_report = kwargs.pop('gap_report', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les types d'écart selon la source d'audit
        if self.gap_report and hasattr(self.gap_report, 'audit_source'):
            self.fields['gap_type'].queryset = GapType.objects.filter(
                audit_source=self.gap_report.audit_source,
                is_active=True
            )
        else:
            self.fields['gap_type'].queryset = GapType.objects.none()
        
        # Filtrer les statuts disponibles selon les droits de l'utilisateur
        if self.instance.pk and self.user:
            # Pour la modification d'un écart existant
            available_statuses = self.instance.get_available_statuses_for_user(self.user)
            self.fields['status'].choices = available_statuses
        elif not self.instance.pk:
            # Pour la création d'un nouvel écart, seul "Déclaré" est disponible
            self.fields['status'].choices = [('declared', 'Déclaré')]
            self.fields['status'].initial = 'declared'

    def clean_gap_type(self):
        gap_type = self.cleaned_data.get('gap_type')
        
        if gap_type and self.gap_report and hasattr(self.gap_report, 'audit_source'):
            if gap_type.audit_source != self.gap_report.audit_source:
                raise ValidationError(
                    'Le type d\'écart doit correspondre à la source d\'audit de la déclaration.'
                )
        
        return gap_type


class GapAttachmentForm(forms.ModelForm):
    """
    Formulaire pour ajouter une pièce jointe à un écart.
    """
    
    class Meta:
        model = GapAttachment
        fields = ['name', 'file']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'placeholder': 'Nom descriptif de la pièce jointe'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.txt,.csv'
            })
        }
        labels = {
            'name': 'Nom de la pièce jointe *',
            'file': 'Fichier *'
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Vérifier la taille du fichier (5MB max)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError('La taille du fichier ne peut pas dépasser 5 Mo.')
        return file