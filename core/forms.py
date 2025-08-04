"""
Formulaires pour la gestion des écarts.
"""
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

from core.models import GapReport, Gap, AuditSource, Service, Process, GapType


class GapReportForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une déclaration d'écart.
    """
    
    class Meta:
        model = GapReport
        fields = [
            'audit_source', 'source_reference', 'service', 'process',
            'location', 'observation_date', 'involved_users'
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
            'service': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors'}),
            'process': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors'}),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'placeholder': 'Lieu de l\'observation'
            }),
            'observation_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-colors',
                'type': 'datetime-local'
            }),
            'involved_users': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            })
        }
        labels = {
            'audit_source': 'Source de l\'audit',
            'source_reference': 'Référence source',
            'service': 'Service concerné',
            'process': 'Processus SMI associé',
            'location': 'Lieu',
            'observation_date': 'Date d\'observation',
            'involved_users': 'Autres utilisateurs impliqués'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Récupérer l'utilisateur connecté
        super().__init__(*args, **kwargs)
        
        # Définir les choix disponibles
        self.fields['audit_source'].queryset = AuditSource.objects.all().order_by('name')
        
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
        
        # Définir la date par défaut
        if not self.instance.pk and 'observation_date' not in self.initial:
            self.fields['observation_date'].initial = datetime.now().strftime('%Y-%m-%dT%H:%M')
        
        # Pré-sélectionner le service de l'utilisateur connecté
        if not self.instance.pk and self.user and self.user.service and 'service' not in self.initial:
            self.fields['service'].initial = self.user.service
        
        # Rendre le champ processus optionnel par défaut
        self.fields['process'].required = False

    def clean(self):
        cleaned_data = super().clean()
        audit_source = cleaned_data.get('audit_source')
        process = cleaned_data.get('process')
        
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
            'gap_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Décrivez l\'écart et ses causes...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'gap_type': 'Type d\'écart (Quoi) *',
            'description': 'Description (Pourquoi) *',
            'status': 'Statut *'
        }

    def __init__(self, *args, **kwargs):
        self.gap_report = kwargs.pop('gap_report', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les types d'écart selon la source d'audit
        if self.gap_report and hasattr(self.gap_report, 'audit_source'):
            self.fields['gap_type'].queryset = GapType.objects.filter(
                audit_source=self.gap_report.audit_source
            )
        else:
            self.fields['gap_type'].queryset = GapType.objects.none()

    def clean_gap_type(self):
        gap_type = self.cleaned_data.get('gap_type')
        
        if gap_type and self.gap_report and hasattr(self.gap_report, 'audit_source'):
            if gap_type.audit_source != self.gap_report.audit_source:
                raise ValidationError(
                    'Le type d\'écart doit correspondre à la source d\'audit de la déclaration.'
                )
        
        return gap_type