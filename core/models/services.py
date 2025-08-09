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
    actif = models.BooleanField(
        default=True, 
        verbose_name="Service actif",
        help_text="Un service inactif reste dans l'historique mais n'apparaît plus dans les listes de sélection"
    )
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
    
    def get_active_descendants(self):
        """Retourne tous les descendants actifs dans la hiérarchie."""
        descendants = []
        for sous_service in self.sous_services.filter(actif=True):
            descendants.append(sous_service)
            descendants.extend(sous_service.get_active_descendants())
        return descendants
    
    def has_active_descendants(self):
        """Vérifie si le service a des descendants actifs."""
        return self.sous_services.filter(actif=True).exists()
    
    def can_be_deactivated(self):
        """
        Vérifie si le service peut être désactivé.
        Un service ne peut pas être désactivé s'il a :
        - Des sous-services actifs
        - Des utilisateurs actifs associés
        - Des déclarations d'écarts associées (GapReport)
        """
        # Vérifier les sous-services actifs
        if self.has_active_descendants():
            return False
        
        # Vérifier les utilisateurs actifs associés
        from .users import User  # Import local pour éviter les imports circulaires
        if User.objects.filter(service=self, actif=True).exists():
            return False
        
        # Vérifier les déclarations d'écarts associées
        from .gaps import GapReport  # Import local pour éviter les imports circulaires
        if GapReport.objects.filter(service=self).exists():
            return False
            
        return True
    
    def get_deactivation_blocking_reason(self):
        """
        Retourne la raison pour laquelle le service ne peut pas être désactivé.
        Utilisé pour afficher des messages d'erreur informatifs.
        """
        reasons = []
        
        # Vérifier les sous-services actifs
        if self.has_active_descendants():
            active_children_count = self.sous_services.filter(actif=True).count()
            reasons.append(f"contient {active_children_count} sous-service(s) actif(s)")
        
        # Vérifier les utilisateurs actifs associés
        from .users import User  # Import local pour éviter les imports circulaires
        active_users_count = User.objects.filter(service=self, actif=True).count()
        if active_users_count > 0:
            reasons.append(f"a {active_users_count} utilisateur(s) actif(s) associé(s)")
        
        # Vérifier les déclarations d'écarts associées
        from .gaps import GapReport  # Import local pour éviter les imports circulaires
        gap_reports_count = GapReport.objects.filter(service=self).count()
        if gap_reports_count > 0:
            reasons.append(f"est associé à {gap_reports_count} déclaration(s) d'écart(s)")
        
        if reasons:
            return f"Le service ne peut pas être désactivé car il {' et '.join(reasons)}."
        
        return None