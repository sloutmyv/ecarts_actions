"""
Modèles pour la gestion des écarts et des audits.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .base import TimestampedModel, CodedModel
from .services import Service

User = get_user_model()


class AuditSource(TimestampedModel):
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

    class Meta:
        verbose_name = "3.1 Source d'audit"
        verbose_name_plural = "3.1 Sources d'audit"
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
        verbose_name = "3.2 Processus SMI"
        verbose_name_plural = "3.2 Processus SMI"
        ordering = ['name']

    def __str__(self):
        return self.name


class GapType(TimestampedModel):
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

    class Meta:
        verbose_name = "3.3 Type d'écart"
        verbose_name_plural = "3.3 Types d'écart"
        ordering = ['audit_source__name', 'name']

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
        verbose_name="Processus SMI associé",
        help_text="Obligatoire uniquement pour les audits internes"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Lieu"
    )
    observation_date = models.DateTimeField(
        verbose_name="Date et heure d'observation"
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
        verbose_name = "3. Déclaration d'écart"
        verbose_name_plural = "3. Déclarations d'écart"
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
        return f"Déclaration #{self.id} - {self.audit_source.name} - {self.observation_date}"


class Gap(TimestampedModel):
    """
    Écart individuel associé à une déclaration.
    """
    
    STATUS_CHOICES = [
        ('declared', 'Déclaré'),
        ('cancelled', 'Annulé'),
        ('retained', 'Retenu'),
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
        # Éviter la validation si gap_report n'est pas encore assigné
        if (self.gap_type and self.gap_report_id and hasattr(self, 'gap_report')):
            try:
                gap_report = self.gap_report
                if self.gap_type.audit_source != gap_report.audit_source:
                    raise ValidationError({
                        'gap_type': 'Le type d\'écart doit correspondre à la source d\'audit de la déclaration.'
                    })
            except GapReport.DoesNotExist:
                # Si gap_report n'existe pas encore, ignorer la validation
                pass

    def save(self, *args, **kwargs):
        """
        Génère automatiquement un numéro d'écart si non fourni.
        Format: [ID_DECLARATION].[NUMERO_ECART]
        """
        if not self.gap_number and self.gap_report_id:
            # Utiliser une transaction pour éviter les conflits de concurrence
            from django.db import transaction
            with transaction.atomic():
                # Verrouiller la table pour éviter les conditions de course
                existing_gaps = Gap.objects.select_for_update().filter(
                    gap_report_id=self.gap_report_id
                ).order_by('gap_number')
                
                # Trouver le prochain numéro disponible
                next_gap_number = 1
                for gap in existing_gaps:
                    # Extraire le numéro d'écart à partir du gap_number (format: "ID.NUMERO")
                    try:
                        gap_num = int(gap.gap_number.split('.')[-1])
                        if gap_num == next_gap_number:
                            next_gap_number += 1
                        elif gap_num > next_gap_number:
                            # On a trouvé un "trou" dans la numérotation
                            break
                    except (ValueError, IndexError):
                        # Si le format n'est pas standard, ignorer
                        continue
                
                # Format: ID_DECLARATION.NUMERO_ECART
                self.gap_number = f'{self.gap_report_id}.{next_gap_number}'
        
        super().save(*args, **kwargs)

    def is_visible_to_user(self, user):
        """
        Détermine si un écart est visible pour un utilisateur donné.
        
        Règles de visibilité :
        - Écarts annulés : visibles seulement par le déclarant et les administrateurs (SA/AD)
        - Autres statuts : visibles par tous les utilisateurs
        """
        if self.status == 'cancelled':
            # Écart annulé : visible seulement par le déclarant et les administrateurs
            return (
                self.gap_report.declared_by == user or 
                user.droits in ['SA', 'AD']
            )
        # Autres statuts : visibles par tous
        return True
    
    def get_available_statuses_for_user(self, user):
        """
        Retourne les statuts disponibles pour un utilisateur donné.
        
        Règles d'accès aux statuts :
        - Déclarant : peut passer de 'déclaré' à 'annulé' uniquement
        - SA/AD : accès à tous les statuts
        - Valideur (à définir plus tard) : accès aux statuts administratifs
        """
        if user.droits in ['SA', 'AD']:
            # Administrateurs : tous les statuts
            return self.STATUS_CHOICES
        elif self.gap_report.declared_by == user:
            # Déclarant : peut seulement annuler son écart
            if self.status == 'declared':
                return [
                    ('declared', 'Déclaré'),
                    ('cancelled', 'Annulé'),
                ]
            else:
                # Si l'écart n'est plus à l'état "déclaré", le déclarant ne peut plus le modifier
                return [(self.status, dict(self.STATUS_CHOICES)[self.status])]
        else:
            # Autres utilisateurs : lecture seule
            return [(self.status, dict(self.STATUS_CHOICES)[self.status])]

    def __str__(self):
        return f"{self.gap_number} - {self.gap_type.name}"