"""
Modèles liés à la gestion des services et de l'organisation hiérarchique.
"""
from django.db import models
from django.core.exceptions import ValidationError
from .base import TimestampedModel, CodedModel


class Service(TimestampedModel, CodedModel):
    """
    Modèle représentant un service/département dans l'organisation.
    Supporte une hiérarchie illimitée avec relations parent-enfant.
    """
    nom = models.CharField(max_length=100, verbose_name="Nom du service")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sous_services',
        verbose_name="Service parent"
    )
    
    class Meta:
        verbose_name = "1. Service"
        verbose_name_plural = "1. Services"
        ordering = ['nom']
        
    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    def clean(self):
        """Validation des relations hiérarchiques."""
        if self.parent and self.parent == self:
            raise ValidationError("Un service ne peut pas être son propre parent.")
        
        if self.parent and self._check_circular_dependency(self.parent):
            raise ValidationError("Cette relation créerait une dépendance circulaire.")
    
    def _check_circular_dependency(self, parent):
        """Vérifie s'il y a une dépendance circulaire dans la hiérarchie."""
        if parent == self:
            return True
        if parent.parent:
            return self._check_circular_dependency(parent.parent)
        return False
    
    def get_niveau(self):
        """Retourne le niveau hiérarchique (0 = racine)."""
        niveau = 0
        current = self.parent
        while current:
            niveau += 1
            current = current.parent
        return niveau
    
    def get_chemin_hierarchique(self):
        """Retourne le chemin hiérarchique complet (ex: 'DG > DRH > REC')."""
        chemin = [self.nom]
        current = self.parent
        while current:
            chemin.insert(0, current.nom)
            current = current.parent
        return " > ".join(chemin)
    
    def get_tous_sous_services_ordonnes(self):
        """Retourne tous les sous-services ordonnés par nom de façon récursive."""
        sous_services = list(self.sous_services.order_by('nom'))
        result = []
        for sous_service in sous_services:
            result.append(sous_service)
            result.extend(sous_service.get_tous_sous_services_ordonnes())
        return result
    
    def get_descendants(self):
        """Retourne tous les descendants dans la hiérarchie."""
        descendants = []
        for sous_service in self.sous_services.all():
            descendants.append(sous_service)
            descendants.extend(sous_service.get_descendants())
        return descendants
    
    def get_descendants_count(self):
        """Retourne le nombre total de descendants (tous niveaux confondus)."""
        count = 0
        for sous_service in self.sous_services.all():
            count += 1  # Compter le sous-service direct
            count += sous_service.get_descendants_count()  # Compter ses descendants
        return count
    
    def is_racine(self):
        """Vérifie si le service est un service racine (sans parent)."""
        return self.parent is None