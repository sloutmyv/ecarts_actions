"""
Modèles liés à la gestion des utilisateurs et de l'authentification.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .base import TimestampedModel
from .services import Service


class CustomUserManager(BaseUserManager):
    """
    Manager personnalisé pour le modèle User avec authentification par matricule.
    """
    def create_user(self, matricule, email=None, password=None, **extra_fields):
        """
        Crée et sauvegarde un utilisateur avec le matricule et mot de passe donnés.
        Si aucun mot de passe n'est fourni, utilise "azerty" par défaut.
        """
        if not matricule:
            raise ValueError('Le matricule est obligatoire')
        
        matricule = matricule.upper()
        if email:
            email = self.normalize_email(email)
        
        # Si aucun mot de passe fourni, utiliser "azerty" par défaut
        if password is None:
            password = 'azerty'
            extra_fields.setdefault('must_change_password', True)
        
        user = self.model(matricule=matricule, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricule, email=None, password=None, **extra_fields):
        """
        Crée et sauvegarde un super utilisateur avec les privilèges donnés.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('droits', User.SUPER_ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Un superuser doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Un superuser doit avoir is_superuser=True.')

        return self.create_user(matricule, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """
    Modèle d'utilisateur personnalisé avec authentification par matricule.
    """
    # Choix pour les droits utilisateur
    SUPER_ADMIN = 'SA'
    ADMIN = 'AD'
    USER = 'US'
    
    DROITS_CHOICES = [
        (SUPER_ADMIN, 'Super Administrateur'),
        (ADMIN, 'Administrateur'),
        (USER, 'Utilisateur'),
    ]
    
    # Validateur pour le matricule (1 lettre + 4 chiffres)
    matricule_validator = RegexValidator(
        regex=r'^[A-Z][0-9]{4}$',
        message='Le matricule doit contenir une lettre majuscule suivie de 4 chiffres (ex: A1234)'
    )
    
    matricule = models.CharField(
        max_length=5,
        unique=True,
        validators=[matricule_validator],
        verbose_name="Matricule",
        help_text="Format: 1 lettre + 4 chiffres (ex: A1234)"
    )
    nom = models.CharField(max_length=50, verbose_name="Nom")
    prenom = models.CharField(max_length=50, verbose_name="Prénom")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    droits = models.CharField(
        max_length=2,
        choices=DROITS_CHOICES,
        default=USER,
        verbose_name="Droits d'accès"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Service"
    )
    
    # Champs pour Django Auth
    is_staff = models.BooleanField(default=False, verbose_name="Membre du staff")
    must_change_password = models.BooleanField(
        default=True, 
        verbose_name="Doit changer le mot de passe"
    )
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'matricule'
    REQUIRED_FIELDS = ['nom', 'prenom']
    
    class Meta:
        verbose_name = "2. Utilisateur"
        verbose_name_plural = "2. Utilisateurs"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.matricule} - {self.get_full_name()}"
    
    def clean(self):
        """Validation personnalisée."""
        super().clean()
        # Convertir le matricule en majuscules
        if self.matricule:
            self.matricule = self.matricule.upper()
    
    def save(self, *args, **kwargs):
        """Sauvegarde avec logique métier."""
        # Définir is_staff basé sur les droits
        if self.droits in [self.SUPER_ADMIN, self.ADMIN]:
            self.is_staff = True
        else:
            self.is_staff = False
            
        # Définir is_superuser pour les Super Admins
        if self.droits == self.SUPER_ADMIN:
            self.is_superuser = True
        else:
            self.is_superuser = False
            
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur."""
        return f"{self.prenom} {self.nom}".strip()
    
    def get_short_name(self):
        """Retourne le prénom de l'utilisateur."""
        return self.prenom
    
    def get_droits_display_badge(self):
        """Retourne une classe CSS pour afficher un badge selon les droits."""
        badge_classes = {
            self.SUPER_ADMIN: 'bg-red-100 text-red-800',
            self.ADMIN: 'bg-blue-100 text-blue-800',
            self.USER: 'bg-green-100 text-green-800',
        }
        return badge_classes.get(self.droits, 'bg-gray-100 text-gray-800')
    
    def can_manage_users(self):
        """Vérifie si l'utilisateur peut gérer d'autres utilisateurs."""
        return self.droits in [self.SUPER_ADMIN, self.ADMIN]
    
    def can_access_admin(self):
        """Vérifie si l'utilisateur peut accéder à l'administration."""
        return self.droits in [self.SUPER_ADMIN, self.ADMIN]
    
    def get_service_path(self):
        """Retourne le chemin hiérarchique du service de l'utilisateur."""
        if self.service:
            return self.service.get_chemin_hierarchique()
        return "Aucun service"