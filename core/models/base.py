"""
Modèles de base et abstraits pour l'application EcartsActions.
Ces modèles peuvent être étendus par d'autres modèles métier.
"""
from django.db import models


class TimestampedModel(models.Model):
    """
    Modèle abstrait fournissant les champs de timestamp automatiques.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        abstract = True


class CodedModel(models.Model):
    """
    Modèle abstrait fournissant un champ code unique.
    """
    code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Code",
        help_text="Code unique pour identifier l'élément"
    )
    
    class Meta:
        abstract = True