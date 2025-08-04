"""
Modèle pour la gestion des pièces jointes.
"""
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .base import TimestampedModel
from .gaps import GapReport, Gap

User = get_user_model()


def gap_report_upload_to(instance, filename):
    """
    Détermine le chemin de stockage pour les pièces jointes de déclaration.
    """
    return f'attachments/gap_reports/{instance.gap_report.id}/{filename}'


def gap_upload_to(instance, filename):
    """
    Détermine le chemin de stockage pour les pièces jointes d'écart.
    """
    return f'attachments/gaps/{instance.gap.gap_number}/{filename}'


class GapReportAttachment(TimestampedModel):
    """
    Pièce jointe associée à une déclaration d'écart.
    """
    gap_report = models.ForeignKey(
        GapReport,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Déclaration d'écart"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de la pièce jointe",
        help_text="Nom descriptif de la pièce jointe"
    )
    file = models.FileField(
        upload_to=gap_report_upload_to,
        verbose_name="Fichier",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 
                                  'jpg', 'jpeg', 'png', 'gif', 'txt', 'csv']
            )
        ]
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Ajouté par"
    )

    class Meta:
        verbose_name = "Pièce jointe de déclaration"
        verbose_name_plural = "Pièces jointes de déclaration"
        ordering = ['-created_at']

    def clean(self):
        """
        Validation de la taille du fichier (max 5Mo).
        """
        if self.file and self.file.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError({
                'file': 'La taille du fichier ne peut pas dépasser 5 Mo.'
            })

    @property
    def file_size_mb(self):
        """
        Retourne la taille du fichier en Mo.
        """
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0

    @property
    def file_extension(self):
        """
        Retourne l'extension du fichier.
        """
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''

    def __str__(self):
        return f"{self.name} - {self.gap_report}"


class GapAttachment(TimestampedModel):
    """
    Pièce jointe associée à un écart individuel.
    """
    gap = models.ForeignKey(
        Gap,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Écart"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de la pièce jointe",
        help_text="Nom descriptif de la pièce jointe"
    )
    file = models.FileField(
        upload_to=gap_upload_to,
        verbose_name="Fichier",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 
                                  'jpg', 'jpeg', 'png', 'gif', 'txt', 'csv']
            )
        ]
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Ajouté par"
    )

    class Meta:
        verbose_name = "Pièce jointe d'écart"
        verbose_name_plural = "Pièces jointes d'écart"
        ordering = ['-created_at']

    def clean(self):
        """
        Validation de la taille du fichier (max 5Mo).
        """
        if self.file and self.file.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError({
                'file': 'La taille du fichier ne peut pas dépasser 5 Mo.'
            })

    @property
    def file_size_mb(self):
        """
        Retourne la taille du fichier en Mo.
        """
        if self.file:
            return round(self.file.size / (1024 * 1024), 2)
        return 0

    @property
    def file_extension(self):
        """
        Retourne l'extension du fichier.
        """
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''

    def __str__(self):
        return f"{self.name} - {self.gap}"