"""
Modèles pour la gestion des écarts et des audits.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Les sources inactives ne sont plus proposées dans les formulaires mais les données existantes sont préservées"
    )

    class Meta:
        verbose_name = "3.1 Source d'audit"
        verbose_name_plural = "3.1 Sources d'audit"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['requires_process']),
            models.Index(fields=['is_active']),
        ]

    def can_be_deactivated(self):
        """
        Vérifie si la source d'audit peut être désactivée.
        Une source d'audit ne peut pas être désactivée si elle a des validateurs associés.
        """
        from .workflow import ValidateurService
        return not ValidateurService.objects.filter(
            audit_source=self,
            actif=True
        ).exists()

    def get_deactivation_blocking_reason(self):
        """
        Retourne la raison pour laquelle la source d'audit ne peut pas être désactivée.
        Utilisé pour afficher des messages d'erreur informatifs.
        """
        from .workflow import ValidateurService
        validateurs_count = ValidateurService.objects.filter(
            audit_source=self,
            actif=True
        ).count()
        
        if validateurs_count > 0:
            return f"La source d'audit ne peut pas être désactivée car elle a {validateurs_count} validateur(s) associé(s)."
        
        return None

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
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name


class GapType(TimestampedModel):
    """
    Type d'événement (Quoi) - entité administrable.
    Chaque type est associé à une source d'audit spécifique.
    Le champ 'is_gap' permet de différencier les événements qui sont des écarts 
    de ceux qui sont de simples événements.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nom du type d'événement"
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
    is_gap = models.BooleanField(
        default=True,
        verbose_name="Écart",
        help_text="Cochez si cet événement constitue un écart. Décochez pour un simple événement."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Les types inactifs ne sont plus proposés dans les formulaires mais les données existantes sont préservées"
    )

    class Meta:
        verbose_name = "3.3 Type d'événement"
        verbose_name_plural = "3.3 Types d'événement"
        ordering = ['audit_source__name', 'name']
        indexes = [
            models.Index(fields=['audit_source', 'name']),
            models.Index(fields=['is_gap']),
            models.Index(fields=['audit_source', 'is_gap']),
            models.Index(fields=['is_active']),
        ]

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
        verbose_name_plural = "3. Déclarations d'évenements"
        ordering = ['-observation_date', '-created_at']
        indexes = [
            models.Index(fields=['-observation_date', '-created_at']),
            models.Index(fields=['audit_source', '-observation_date']),
            models.Index(fields=['service', '-observation_date']),
            models.Index(fields=['declared_by', '-observation_date']),
            models.Index(fields=['process', '-observation_date']),
            models.Index(fields=['audit_source', 'service', '-observation_date']),
        ]

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

    def get_gaps_count(self):
        """
        Retourne le nombre d'écarts (is_gap=True) dans cette déclaration.
        """
        return self.gaps.filter(gap_type__is_gap=True).count()
    
    def get_events_count(self):
        """
        Retourne le nombre d'événements non-écarts (is_gap=False) dans cette déclaration.
        """
        return self.gaps.filter(gap_type__is_gap=False).count()

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
        verbose_name="Type d'événement (Quoi)"
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
        verbose_name = "3.4 Écart"
        verbose_name_plural = "3.4 Écarts"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['gap_report', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['gap_type', '-created_at']),
            models.Index(fields=['gap_number']),
            models.Index(fields=['gap_report', 'status']),
            models.Index(fields=['gap_type', 'status']),
        ]

    def clean(self):
        """
        Validation pour s'assurer que le type d'événement correspond à la source d'audit.
        """
        # Éviter la validation si gap_report n'est pas encore assigné
        if (self.gap_type and self.gap_report_id and hasattr(self, 'gap_report')):
            try:
                gap_report = self.gap_report
                if self.gap_type.audit_source != gap_report.audit_source:
                    raise ValidationError({
                        'gap_type': 'Le type d\'événement doit correspondre à la source d\'audit de la déclaration.'
                    })
            except GapReport.DoesNotExist:
                # Si gap_report n'existe pas encore, ignorer la validation
                pass

    def save(self, *args, **kwargs):
        """
        Génère automatiquement un numéro d'écart si non fourni.
        Format: [ID_DECLARATION].[NUMERO_ECART]
        Optimisé pour les accès concurrents avec retry automatique.
        """
        if not self.gap_number and self.gap_report_id:
            # Utiliser une transaction pour éviter les conflits de concurrence avec retry
            from django.db import transaction, IntegrityError
            import time
            import random
            
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with transaction.atomic():
                        # Utiliser NOWAIT pour éviter les blocages longs en cas de forte concurrence
                        existing_gaps = Gap.objects.select_for_update(nowait=True).filter(
                            gap_report_id=self.gap_report_id
                        ).order_by('gap_number')
                        
                        # Optimisation : utiliser une requête directe pour obtenir le max
                        from django.db.models import Max
                        max_number_result = Gap.objects.filter(
                            gap_report_id=self.gap_report_id
                        ).aggregate(Max('gap_number'))
                        
                        # Extraire le numéro maximum existant
                        next_gap_number = 1
                        if max_number_result['gap_number__max']:
                            try:
                                last_number = max_number_result['gap_number__max'].split('.')[-1]
                                next_gap_number = int(last_number) + 1
                            except (ValueError, IndexError):
                                # Si extraction échoue, utiliser l'ancienne méthode
                                for gap in existing_gaps:
                                    try:
                                        gap_num = int(gap.gap_number.split('.')[-1])
                                        if gap_num >= next_gap_number:
                                            next_gap_number = gap_num + 1
                                    except (ValueError, IndexError):
                                        continue
                        
                        # Format: ID_DECLARATION.NUMERO_ECART
                        self.gap_number = f'{self.gap_report_id}.{next_gap_number}'
                        break  # Sortir de la boucle si succès
                        
                except IntegrityError:
                    # En cas de conflit, retry avec backoff exponentiel + jitter
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise  # Re-lancer l'erreur si toutes les tentatives ont échoué
                    
                    # Attendre avant de réessayer (backoff exponentiel avec jitter)
                    sleep_time = (2 ** retry_count) + random.uniform(0, 1)
                    time.sleep(min(sleep_time, 5))  # Maximum 5 secondes
                    
                except Exception:
                    # Pour toute autre exception, utiliser l'ancienne méthode en fallback
                    with transaction.atomic():
                        existing_gaps = Gap.objects.select_for_update().filter(
                            gap_report_id=self.gap_report_id
                        ).order_by('gap_number')
                        
                        next_gap_number = 1
                        for gap in existing_gaps:
                            try:
                                gap_num = int(gap.gap_number.split('.')[-1])
                                if gap_num == next_gap_number:
                                    next_gap_number += 1
                                elif gap_num > next_gap_number:
                                    break
                            except (ValueError, IndexError):
                                continue
                        
                        self.gap_number = f'{self.gap_report_id}.{next_gap_number}'
                    break
        
        super().save(*args, **kwargs)

    def is_visible_to_user(self, user):
        """
        Détermine si un écart est visible pour un utilisateur donné.
        
        Règles de visibilité :
        - Écarts annulés : visibles seulement par le déclarant, les utilisateurs impliqués et les administrateurs (SA/AD)
        - Autres statuts : visibles par tous les utilisateurs
        """
        if self.status == 'cancelled':
            # Écart annulé : visible seulement par le déclarant, les utilisateurs impliqués et les administrateurs
            return (
                self.gap_report.declared_by == user or 
                user in self.gap_report.involved_users.all() or
                user.droits in ['SA', 'AD']
            )
        # Autres statuts : visibles par tous
        return True
    
    def get_available_statuses_for_user(self, user):
        """
        Retourne les statuts disponibles pour un utilisateur donné.
        
        Règles d'accès aux statuts :
        - Pour les événements (non écarts) : seulement "déclaré" et "annulé"
        - Pour les écarts : tous les statuts selon les droits utilisateur
        """
        # Si ce n'est pas un écart, statuts limités
        if not self.gap_type.is_gap:
            if user.droits in ['SA', 'AD'] or self.gap_report.declared_by == user:
                if self.status == 'declared':
                    return [
                        ('declared', 'Déclaré'),
                        ('cancelled', 'Annulé'),
                    ]
                else:
                    # Statut actuel uniquement
                    return [(self.status, dict(self.STATUS_CHOICES)[self.status])]
            else:
                # Autres utilisateurs : lecture seule
                return [(self.status, dict(self.STATUS_CHOICES)[self.status])]
        
        # Pour les vrais écarts : logique existante
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


class HistoriqueModification(TimestampedModel):
    """
    Historique des modifications apportées aux Déclarations d'évenements et aux écarts.
    """
    
    ACTION_CHOICES = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('changement_statut', 'Changement de statut'),
    ]
    
    OBJET_CHOICES = [
        ('gap_report', 'Déclaration d\'écart'),
        ('gap', 'Écart'),
    ]
    
    # Références polymorphiques vers les objets modifiés
    gap_report = models.ForeignKey(
        GapReport,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='historique_modifications',
        verbose_name="Déclaration d'écart"
    )
    gap = models.ForeignKey(
        Gap,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='historique_modifications',
        verbose_name="Écart"
    )
    
    # Informations sur la modification
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    objet_type = models.CharField(
        max_length=20,
        choices=OBJET_CHOICES,
        verbose_name="Type d'objet"
    )
    objet_id = models.PositiveIntegerField(
        verbose_name="ID de l'objet"
    )
    objet_repr = models.CharField(
        max_length=200,
        verbose_name="Représentation de l'objet",
        help_text="Représentation textuelle de l'objet au moment de la modification"
    )
    
    # Utilisateur qui a effectué la modification
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Utilisateur"
    )
    
    # Détails de la modification
    description = models.TextField(
        verbose_name="Description de la modification",
        help_text="Description détaillée des changements effectués"
    )
    donnees_avant = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Données avant modification",
        help_text="État des données avant la modification (format JSON)"
    )
    donnees_apres = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Données après modification",
        help_text="État des données après la modification (format JSON)"
    )
    
    class Meta:
        verbose_name = "Historique de modification"
        verbose_name_plural = "Historiques de modifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['gap_report', '-created_at']),
            models.Index(fields=['gap', '-created_at']),
            models.Index(fields=['objet_type', 'objet_id', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.objet_repr} par {self.utilisateur} le {self.created_at.strftime('%d/%m/%Y à %H:%M')}"
    
    @classmethod
    def enregistrer_modification(cls, objet, action, utilisateur, description, donnees_avant=None, donnees_apres=None):
        """
        Méthode utilitaire pour enregistrer une modification dans l'historique.
        
        Args:
            objet: L'objet modifié (GapReport ou Gap)
            action: Type d'action (creation, modification, suppression, changement_statut)
            utilisateur: Utilisateur qui effectue la modification
            description: Description de la modification
            donnees_avant: Données avant modification (optionnel)
            donnees_apres: Données après modification (optionnel)
        """
        # Déterminer le type d'objet et la déclaration associée
        if isinstance(objet, GapReport):
            objet_type = 'gap_report'
            gap_report = objet
            gap = None
        elif isinstance(objet, Gap):
            objet_type = 'gap'
            gap_report = objet.gap_report
            gap = objet
        else:
            raise ValueError(f"Type d'objet non supporté: {type(objet)}")
        
        return cls.objects.create(
            gap_report=gap_report,
            gap=gap,
            action=action,
            objet_type=objet_type,
            objet_id=objet.id,
            objet_repr=str(objet),
            utilisateur=utilisateur,
            description=description,
            donnees_avant=donnees_avant,
            donnees_apres=donnees_apres
        )


# Signaux pour invalider le cache automatiquement
@receiver(post_save, sender=AuditSource)
@receiver(post_delete, sender=AuditSource)
def invalidate_audit_source_cache(sender, **kwargs):
    """Invalide le cache quand une source d'audit est modifiée ou supprimée."""
    from core.utils.cache import invalidate_reference_data_cache
    invalidate_reference_data_cache()


@receiver(post_save, sender=Process)
@receiver(post_delete, sender=Process)
def invalidate_process_cache(sender, **kwargs):
    """Invalide le cache quand un processus est modifié ou supprimé."""
    from core.utils.cache import invalidate_reference_data_cache
    invalidate_reference_data_cache()


@receiver(post_save, sender=GapType)
@receiver(post_delete, sender=GapType)
def invalidate_gap_type_cache(sender, **kwargs):
    """Invalide le cache quand un type d'événement est modifié ou supprimé."""
    from core.utils.cache import invalidate_reference_data_cache
    invalidate_reference_data_cache()