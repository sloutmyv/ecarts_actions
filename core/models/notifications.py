"""
Modèles pour la gestion des notifications de validation des écarts.
"""
from django.db import models
from django.contrib.auth import get_user_model
from .base import TimestampedModel
from .gaps import Gap

User = get_user_model()


class Notification(TimestampedModel):
    """
    Notification pour la validation des écarts.
    """
    TYPE_CHOICES = [
        ('validation_request', 'Demande de validation'),
        ('validation_approved', 'Validation approuvée'),
        ('validation_rejected', 'Validation rejetée'),
        ('validation_completed', 'Validation effectuée'),
        ('gap_retained', 'Écart retenu'),
        ('gap_rejected', 'Écart non retenu'),
        ('gap_created', 'Écart créé'),
        ('gap_modified', 'Écart modifié'),
        ('gap_deleted', 'Écart supprimé'),
        ('gap_status_changed', 'Statut modifié'),
        ('declaration_involved', 'Impliqué dans une déclaration'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('normal', 'Normale'),
        ('high', 'Haute'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Utilisateur"
    )
    
    gap = models.ForeignKey(
        Gap,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Écart concerné",
        null=True,
        blank=True
    )
    
    gap_report = models.ForeignKey(
        'GapReport',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Déclaration concernée",
        null=True,
        blank=True
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type de notification"
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name="Titre"
    )
    
    message = models.TextField(
        verbose_name="Message"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name="Priorité"
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name="Lu"
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Lu le"
    )
    
    class Meta:
        verbose_name = "5. Notification"
        verbose_name_plural = "5. Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['gap', '-created_at']),
            models.Index(fields=['type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"
    
    def mark_as_read(self):
        """Marque la notification comme lue."""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])


class GapValidation(TimestampedModel):
    """
    Suivi des validations d'écarts par niveau.
    """
    ACTION_CHOICES = [
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    
    gap = models.ForeignKey(
        Gap,
        on_delete=models.CASCADE,
        related_name='validations',
        verbose_name="Écart"
    )
    
    validator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='gap_validations',
        verbose_name="Validateur"
    )
    
    level = models.IntegerField(
        verbose_name="Niveau de validation"
    )
    
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name="Commentaire"
    )
    
    validated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Validé le"
    )
    
    class Meta:
        verbose_name = "5.1 Validation d'écart"
        verbose_name_plural = "5.1 Validations d'écarts"
        ordering = ['-validated_at']
        unique_together = ['gap', 'level']  # Un seul validateur par niveau par écart
        indexes = [
            models.Index(fields=['gap', 'level']),
            models.Index(fields=['validator', '-validated_at']),
            models.Index(fields=['action', '-validated_at']),
        ]
    
    def __str__(self):
        return f"{self.gap} - Niveau {self.level} - {self.get_action_display()}"