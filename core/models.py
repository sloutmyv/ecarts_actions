from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError


class Service(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom du service")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='sous_services',
        verbose_name="Service parent"
    )
    code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Code du service",
        help_text="Code unique pour identifier le service (ex: DRH, COMPTA)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "1. Service"
        verbose_name_plural = "1. Services"
        ordering = ['nom']
        
    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError("Un service ne peut pas être son propre parent.")
        
        if self.parent and self._check_circular_dependency(self.parent):
            raise ValidationError("Cette relation créerait une dépendance circulaire.")
    
    def _check_circular_dependency(self, parent):
        if parent == self:
            return True
        if parent.parent:
            return self._check_circular_dependency(parent.parent)
        return False
    
    def get_niveau(self):
        niveau = 0
        current = self.parent
        while current:
            niveau += 1
            current = current.parent
        return niveau
    
    def get_chemin_hierarchique(self):
        chemin = [self.nom]
        current = self.parent
        while current:
            chemin.insert(0, current.nom)
            current = current.parent
        return " > ".join(chemin)
    
    def get_tous_sous_services_ordonnes(self):
        """Retourne tous les sous-services ordonnés par nom de façon récursive"""
        sous_services = list(self.sous_services.order_by('nom'))
        result = []
        for sous_service in sous_services:
            result.append(sous_service)
            result.extend(sous_service.get_tous_sous_services_ordonnes())
        return result
    
    def get_descendants(self):
        descendants = []
        for sous_service in self.sous_services.all():
            descendants.append(sous_service)
            descendants.extend(sous_service.get_descendants())
        return descendants
    
    def is_racine(self):
        return self.parent is None
