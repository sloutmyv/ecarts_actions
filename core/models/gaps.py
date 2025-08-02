"""
Modèles pour la gestion des écarts et des audits.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .base import TimestampedModel, CodedModel
from .services import Service

User = get_user_model()


class AuditSource(CodedModel, TimestampedModel):
    """
    Source d'audit - entité administrable.
    Exemples: Audit interne, Audit client, Inspection visuelle, Retour client
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nom de la source"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    requires_process = models.BooleanField(
        default=False,
        verbose_name="Nécessite un processus",
        help_text="Si coché, un processus sera obligatoire pour cette source"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    class Meta:
        verbose_name = "Source d'audit"
        verbose_name_plural = "Sources d'audit"
        ordering = ['name']

    def __str__(self):
        return self.name


# Le modèle Department est remplacé par le modèle Service existant


class Process(CodedModel, TimestampedModel):
    """
    Processus - entité administrable.
    Utilisé uniquement pour les audits internes.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nom du processus"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    class Meta:
        verbose_name = "Processus"
        verbose_name_plural = "Processus"
        ordering = ['name']

    def __str__(self):
        return self.name


class GapType(CodedModel, TimestampedModel):
    """
    Type d'écart (Quoi) - entité administrable.
    Chaque type est associé à une source d'audit spécifique.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nom du type d'écart"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    audit_source = models.ForeignKey(
        AuditSource,
        on_delete=models.CASCADE,
        related_name='gap_types',
        verbose_name="Source d'audit"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    class Meta:
        verbose_name = "Type d'écart"
        verbose_name_plural = "Types d'écart"
        ordering = ['audit_source__name', 'name']
        unique_together = ['code', 'audit_source']

    def __str__(self):
        return f"{self.audit_source.name} - {self.name}"


class GapReport(TimestampedModel):
    """
    Entête de déclaration d'écart.
    Regroupe les informations de contexte pour un ou plusieurs écarts.
    """
    audit_source = models.ForeignKey(
        AuditSource,
        on_delete=models.PROTECT,
        verbose_name="Source de l'audit"
    )
    source_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Référence source",
        help_text="Numéro d'audit, référence interne..."
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        null=True,  # Temporaire - sera rendu obligatoire plus tard
        verbose_name="Service concerné"
    )
    process = models.ForeignKey(
        Process,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Processus associé",
        help_text="Obligatoire uniquement pour les audits internes"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Lieu"
    )
    observation_date = models.DateField(
        verbose_name="Date d'observation"
    )
    declared_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='declared_gap_reports',
        verbose_name="Déclaré par"
    )
    involved_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='involved_gap_reports',
        verbose_name="Autres utilisateurs impliqués"
    )

    class Meta:
        verbose_name = "Déclaration d'écart"
        verbose_name_plural = "Déclarations d'écart"
        ordering = ['-observation_date', '-created_at']

    def clean(self):
        """
        Validation personnalisée pour les règles métier.
        """
        if self.audit_source and self.audit_source.requires_process and not self.process:
            raise ValidationError({
                'process': 'Un processus est obligatoire pour cette source d\'audit.'
            })
        
        if self.audit_source and not self.audit_source.requires_process and self.process:
            raise ValidationError({
                'process': 'Aucun processus ne doit être sélectionné pour cette source d\'audit.'
            })

    def __str__(self):
        return f"Déclaration {self.id} - {self.audit_source.name} - {self.observation_date}"


class Gap(TimestampedModel):
    """
    Écart individuel associé à une déclaration.
    """
    
    STATUS_CHOICES = [
        ('declared', 'Déclaré'),
        ('rejected', 'Non retenu'),
        ('closed', 'Clos'),
    ]

    gap_report = models.ForeignKey(
        GapReport,
        on_delete=models.CASCADE,
        related_name='gaps',
        verbose_name="Déclaration d'écart"
    )
    gap_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numéro d'écart",
        help_text="Identifiant unique de l'écart (ex: EC-2024-0001)"
    )
    gap_type = models.ForeignKey(
        GapType,
        on_delete=models.PROTECT,
        verbose_name="Type d'écart (Quoi)"
    )
    description = models.TextField(
        verbose_name="Pourquoi (justification/explication)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='declared',
        verbose_name="Statut"
    )

    class Meta:
        verbose_name = "Écart"
        verbose_name_plural = "Écarts"
        ordering = ['-created_at']

    def clean(self):
        """
        Validation pour s'assurer que le type d'écart correspond à la source d'audit.
        """
        if (self.gap_type and self.gap_report and 
            self.gap_type.audit_source != self.gap_report.audit_source):
            raise ValidationError({
                'gap_type': 'Le type d\'écart doit correspondre à la source d\'audit de la déclaration.'
            })

    def save(self, *args, **kwargs):
        """
        Génère automatiquement un numéro d'écart si non fourni.
        """
        if not self.gap_number:
            # Format: EC-YYYY-XXXX
            from datetime import datetime
            year = datetime.now().year
            last_gap = Gap.objects.filter(
                gap_number__startswith=f'EC-{year}-'
            ).order_by('gap_number').last()
            
            if last_gap:
                last_number = int(last_gap.gap_number.split('-')[-1])
                next_number = last_number + 1
            else:
                next_number = 1
            
            self.gap_number = f'EC-{year}-{next_number:04d}'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.gap_number} - {self.gap_type.name}"