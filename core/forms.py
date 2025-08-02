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
                'class': 'form-select',
                'hx-get': '/gaps/api/process-field/',
                'hx-target': '#process-field',
                'hx-include': '[name="audit_source"]'
            }),
            'source_reference': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Référence optionnelle'
            }),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'process': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Lieu de l\'observation'
            }),
            'observation_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'involved_users': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            })
        }
        labels = {
            'audit_source': 'Source de l\'audit *',
            'source_reference': 'Référence source',
            'service': 'Service concerné *',
            'process': 'Processus associé',
            'location': 'Lieu',
            'observation_date': 'Date d\'observation *',
            'involved_users': 'Autres utilisateurs impliqués'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Récupérer l'utilisateur connecté
        super().__init__(*args, **kwargs)
        
        # Filtrer les choix actifs uniquement
        self.fields['audit_source'].queryset = AuditSource.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.all().order_by('nom')
        self.fields['process'].queryset = Process.objects.filter(is_active=True)
        
        # Définir la date par défaut
        if not self.instance.pk and 'observation_date' not in self.initial:
            self.fields['observation_date'].initial = datetime.now().date()
        
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
        if self.gap_report:
            self.fields['gap_type'].queryset = GapType.objects.filter(
                audit_source=self.gap_report.audit_source,
                is_active=True
            )
        else:
            self.fields['gap_type'].queryset = GapType.objects.none()

    def clean_gap_type(self):
        gap_type = self.cleaned_data.get('gap_type')
        
        if gap_type and self.gap_report:
            if gap_type.audit_source != self.gap_report.audit_source:
                raise ValidationError(
                    'Le type d\'écart doit correspondre à la source d\'audit de la déclaration.'
                )
        
        return gap_type