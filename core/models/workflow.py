"""
Modèles liés à la gestion du workflow de validation des écarts.
"""
from django.db import models
from django.core.exceptions import ValidationError
from .base import TimestampedModel
from .services import Service
from .users import User


class ValidateurService(TimestampedModel):
    """
    Modèle pour assigner des valideurs à des services avec des niveaux de validation.
    Permet de définir qui peut valider les écarts d'un service donné à quel niveau.
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
    
    validateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='services_valides',
        verbose_name="Validateur",
        limit_choices_to={'droits__in': [User.ADMIN, User.SUPER_ADMIN]}
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
        ordering = ['service__nom', 'niveau']
        unique_together = ['service', 'validateur', 'niveau']
        
    def __str__(self):
        return f"{self.service.nom} - {self.validateur.get_full_name()} (Niveau {self.niveau})"
    
    def clean(self):
        """Validation des règles métier."""
        super().clean()
        
        # Vérifier que le validateur a les droits nécessaires
        if self.validateur and self.validateur.droits not in [User.ADMIN, User.SUPER_ADMIN]:
            raise ValidationError({
                'validateur': 'Seuls les administrateurs peuvent être validateurs.'
            })
    
    @classmethod
    def get_validateurs_service(cls, service, niveau=None, actif_seulement=True):
        """
        Retourne les validateurs d'un service donné, optionnellement filtrés par niveau.
        
        Args:
            service: Instance de Service
            niveau: Niveau de validation (optionnel)
            actif_seulement: Si True, ne retourne que les validateurs actifs
        
        Returns:
            QuerySet des ValidateurService
        """
        queryset = cls.objects.filter(service=service)
        
        if niveau is not None:
            queryset = queryset.filter(niveau=niveau)
            
        if actif_seulement:
            queryset = queryset.filter(actif=True)
            
        return queryset.select_related('validateur', 'service')
    
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