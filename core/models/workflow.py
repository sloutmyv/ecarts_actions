"""
Modèles liés à la gestion du workflow de validation des écarts.
"""
from django.db import models
from django.core.exceptions import ValidationError
from .base import TimestampedModel
from .services import Service
from .users import User
from .gaps import AuditSource


class ValidateurService(TimestampedModel):
    """
    Modèle pour assigner des valideurs à des services avec des niveaux de validation
    pour des sources d'audit spécifiques.
    Permet de définir qui peut valider les écarts d'un service donné à quel niveau
    pour une source d'audit donnée.
    """
    NIVEAU_1 = 1
    NIVEAU_2 = 2
    NIVEAU_3 = 3
    
    NIVEAU_CHOICES = [
        (NIVEAU_1, 'Niveau 1'),
        (NIVEAU_2, 'Niveau 2'),
        (NIVEAU_3, 'Niveau 3'),
    ]
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='validateurs',
        verbose_name="Service"
    )
    
    audit_source = models.ForeignKey(
        AuditSource,
        on_delete=models.CASCADE,
        related_name='validateurs',
        verbose_name="Source d'audit",
        default=1  # Audit interne/AFNOR par défaut pour les enregistrements existants
    )
    
    validateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='services_valides',
        verbose_name="Validateur"
    )
    
    niveau = models.IntegerField(
        choices=NIVEAU_CHOICES,
        verbose_name="Niveau de validation"
    )
    
    actif = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Décocher pour désactiver temporairement cette affectation"
    )
    
    class Meta:
        verbose_name = "Validateur de service"
        verbose_name_plural = "Validateurs de service"
        ordering = ['service__nom', 'audit_source__name', 'niveau']
        unique_together = ['service', 'audit_source', 'niveau']
        
    def __str__(self):
        return f"{self.service.nom} - {self.audit_source.name} - {self.validateur.get_full_name()} (Niveau {self.niveau})"
    
    def clean(self):
        """Validation des règles métier."""
        super().clean()
        
        
        # Vérifier qu'il n'y a qu'un seul validateur par niveau par service par source d'audit
        if self.service and self.audit_source and self.niveau:
            existing = ValidateurService.objects.filter(
                service=self.service,
                audit_source=self.audit_source,
                niveau=self.niveau,
                actif=True
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError({
                    'validateur': f'Un validateur est déjà assigné au niveau {self.niveau} '
                                f'pour ce service et cette source d\'audit.'
                })
    
    @classmethod
    def get_validateurs_service(cls, service, audit_source=None, niveau=None, actif_seulement=True):
        """
        Retourne les validateurs d'un service donné, optionnellement filtrés par source d'audit et niveau.
        
        Args:
            service: Instance de Service
            audit_source: Instance d'AuditSource (optionnel)
            niveau: Niveau de validation (optionnel)
            actif_seulement: Si True, ne retourne que les validateurs actifs
        
        Returns:
            QuerySet des ValidateurService
        """
        queryset = cls.objects.filter(service=service)
        
        if audit_source is not None:
            queryset = queryset.filter(audit_source=audit_source)
        
        if niveau is not None:
            queryset = queryset.filter(niveau=niveau)
            
        if actif_seulement:
            queryset = queryset.filter(actif=True)
            
        return queryset.select_related('validateur', 'service', 'audit_source')
    
    @classmethod
    def get_services_validateur(cls, validateur, actif_seulement=True):
        """
        Retourne tous les services qu'un validateur peut valider.
        
        Args:
            validateur: Instance de User
            actif_seulement: Si True, ne retourne que les affectations actives
            
        Returns:
            QuerySet des ValidateurService
        """
        queryset = cls.objects.filter(validateur=validateur)
        
        if actif_seulement:
            queryset = queryset.filter(actif=True)
            
        return queryset.select_related('validateur', 'service')
    
    @classmethod
    def get_niveaux_max_service(cls, service):
        """
        Retourne le niveau maximum de validation configuré pour un service.
        
        Args:
            service: Instance de Service
            
        Returns:
            int: Niveau maximum ou 0 si aucun validateur
        """
        max_niveau = cls.objects.filter(
            service=service, 
            actif=True
        ).aggregate(
            max_niveau=models.Max('niveau')
        )['max_niveau']
        
        return max_niveau or 0