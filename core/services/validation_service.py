"""
Service pour gérer le workflow de validation des écarts.
"""
from django.db import transaction
from django.utils import timezone
from ..models import Gap, ValidateurService, Notification, GapValidation


class ValidationService:
    """
    Service pour gérer le workflow de validation des écarts.
    """
    
    @classmethod
    def create_gap_notification(cls, gap):
        """
        Crée une notification pour le premier validateur quand un écart est déclaré.
        
        Args:
            gap: Instance de Gap nouvellement créé
        """
        if gap.status != 'declared' or not gap.gap_type.is_gap:
            return
        
        # Trouver le validateur de niveau 1
        validators = ValidateurService.get_validateurs_service(
            service=gap.gap_report.service,
            audit_source=gap.gap_report.audit_source,
            niveau=1,
            actif_seulement=True
        )
        
        if validators.exists():
            validator = validators.first()
            cls._create_notification(
                user=validator.validateur,
                gap=gap,
                type='validation_request',
                title=f"{gap.gap_number} - Nouvel événement à valider",
                message=f"Un nouvel écart ({gap.gap_number}) a été déclaré par {gap.gap_report.declared_by.get_full_name()} "
                       f"et nécessite votre validation (Niveau 1).\n\n"
                       f"Service: {gap.gap_report.service.nom}\n"
                       f"Type: {gap.gap_type.name}\n"
                       f"Description: {gap.description[:100]}...",
                priority='normal'
            )
    
    @classmethod
    def validate_gap(cls, gap, validator, action, comment="", level=None):
        """
        Valide ou rejette un écart.
        
        Args:
            gap: Instance de Gap
            validator: Instance de User (validateur)
            action: 'approved' ou 'rejected'
            comment: Commentaire de validation (optionnel)
            level: Niveau de validation (auto-détecté si None)
        
        Returns:
            bool: True si la validation est terminée (retenu/rejeté final)
        """
        if gap.status not in ['declared']:
            raise ValueError("L'écart ne peut plus être validé")
        
        with transaction.atomic():
            # Déterminer le niveau de validation si pas fourni
            if level is None:
                level = cls._get_validator_level(gap, validator)
                if level is None:
                    raise ValueError("Vous n'êtes pas autorisé à valider cet écart")
            
            # Créer l'enregistrement de validation
            validation = GapValidation.objects.create(
                gap=gap,
                validator=validator,
                level=level,
                action=action,
                comment=comment
            )
            
            # Si rejet, l'écart est définitivement rejeté
            if action == 'rejected':
                gap.status = 'rejected'
                gap.save(update_fields=['status', 'updated_at'])
                
                # Marquer comme lues les notifications de validation pour ce validateur
                cls._mark_validation_notifications_read(gap, validator)
                
                # Notifier le déclarant
                cls._create_notification(
                    user=gap.gap_report.declared_by,
                    gap=gap,
                    type='gap_rejected',
                    title=f"{gap.gap_number} - Événement rejeté",
                    message=f"Votre événement {gap.gap_number} a été rejeté au niveau {level} par {validator.get_full_name()}.\n"
                           f"Commentaire: {comment}" if comment else f"Votre événement {gap.gap_number} a été rejeté au niveau {level} par {validator.get_full_name()}.",
                    priority='high'
                )
                
                # Créer une notification pour le validateur confirmant son action
                cls._create_notification(
                    user=validator,
                    gap=gap,
                    type='validation_completed',
                    title=f"{gap.gap_number} - Traitement effectué : Non retenu",
                    message=f"Vous avez rejeté l'événement {gap.gap_number}. Le déclarant a été notifié.",
                    priority='normal'
                )
                return True
            
            # Si approbation, vérifier s'il faut passer au niveau suivant
            elif action == 'approved':
                max_level = cls._get_max_validation_level(gap)
                
                if level >= max_level:
                    # Validation terminée, écart retenu
                    gap.status = 'retained'
                    gap.save(update_fields=['status', 'updated_at'])
                    
                    # Marquer comme lues les notifications de validation pour ce validateur
                    cls._mark_validation_notifications_read(gap, validator)
                    
                    # Notifier le déclarant
                    cls._create_notification(
                        user=gap.gap_report.declared_by,
                        gap=gap,
                        type='gap_retained',
                        title=f"{gap.gap_number} - Événement retenu",
                        message=f"Votre événement {gap.gap_number} a été retenu après validation complète par {validator.get_full_name()}.",
                        priority='high'
                    )
                    
                    # Créer une notification pour le validateur confirmant son action
                    cls._create_notification(
                        user=validator,
                        gap=gap,
                        type='validation_completed',
                        title=f"{gap.gap_number} - Traitement effectué : Retenu",
                        message=f"Vous avez approuvé l'événement {gap.gap_number}. L'événement est maintenant retenu et le déclarant a été notifié.",
                        priority='normal'
                    )
                    return True
                else:
                    # Passer au niveau suivant
                    next_level = level + 1
                    
                    # Marquer comme lues les notifications de validation pour ce validateur
                    cls._mark_validation_notifications_read(gap, validator)
                    
                    # Créer une notification pour le validateur confirmant son action
                    cls._create_notification(
                        user=validator,
                        gap=gap,
                        type='validation_completed',
                        title=f"{gap.gap_number} - Traitement effectué : Approuvé",
                        message=f"Vous avez approuvé l'événement {gap.gap_number}. Il passe maintenant au niveau {next_level}.",
                        priority='normal'
                    )
                    
                    next_validators = ValidateurService.get_validateurs_service(
                        service=gap.gap_report.service,
                        audit_source=gap.gap_report.audit_source,
                        niveau=next_level,
                        actif_seulement=True
                    )
                    
                    if next_validators.exists():
                        next_validator = next_validators.first()
                        cls._create_notification(
                            user=next_validator.validateur,
                            gap=gap,
                            type='validation_request',
                            title=f"{gap.gap_number} - Événement à valider (Niveau {next_level})",
                            message=f"L'écart {gap.gap_number} a été approuvé au niveau {level} par {validator.get_full_name()} "
                                   f"et nécessite maintenant votre validation (Niveau {next_level}).\n\n"
                                   f"Service: {gap.gap_report.service.nom}\n"
                                   f"Type: {gap.gap_type.name}\n"
                                   f"Description: {gap.description[:100]}...",
                            priority='normal'
                        )
                    
                    return False
        
        return False
    
    @classmethod
    def get_pending_validations(cls, validator):
        """
        Retourne les écarts en attente de validation pour un validateur.
        
        Args:
            validator: Instance de User
            
        Returns:
            QuerySet: Écarts à valider
        """
        # Récupérer les services et sources d'audit que ce validateur peut valider
        validator_assignments = ValidateurService.get_services_validateur(
            validator, actif_seulement=True
        )
        
        pending_gaps = []
        
        for assignment in validator_assignments:
            # Trouver les écarts de ce service/source qui sont au niveau de ce validateur
            gaps = Gap.objects.filter(
                status='declared',
                gap_type__is_gap=True,
                gap_report__service=assignment.service,
                gap_report__audit_source=assignment.audit_source
            ).select_related(
                'gap_report__declared_by',
                'gap_report__service',
                'gap_report__audit_source',
                'gap_type'
            )
            
            for gap in gaps:
                # Vérifier si ce validateur peut valider cet écart maintenant
                if cls._can_validate_now(gap, validator, assignment.niveau):
                    pending_gaps.append(gap)
        
        return pending_gaps
    
    @classmethod
    def _get_validator_level(cls, gap, validator):
        """
        Détermine le niveau de validation d'un validateur pour un écart donné.
        """
        validators = ValidateurService.get_validateurs_service(
            service=gap.gap_report.service,
            audit_source=gap.gap_report.audit_source,
            actif_seulement=True
        ).filter(validateur=validator)
        
        if validators.exists():
            return validators.first().niveau
        return None
    
    @classmethod
    def _get_max_validation_level(cls, gap):
        """
        Retourne le niveau maximum de validation pour un écart.
        """
        return ValidateurService.get_niveaux_max_service(gap.gap_report.service)
    
    @classmethod
    def _can_validate_now(cls, gap, validator, validator_level):
        """
        Vérifie si un validateur peut valider un écart maintenant.
        """
        # Vérifier les validations déjà effectuées
        existing_validations = GapValidation.objects.filter(gap=gap).order_by('level')
        
        if not existing_validations.exists():
            # Aucune validation, seul le niveau 1 peut valider
            return validator_level == 1
        
        last_validation = existing_validations.last()
        
        # Si la dernière validation était un rejet, personne ne peut plus valider
        if last_validation.action == 'rejected':
            return False
        
        # Si la dernière validation était une approbation, 
        # seul le niveau suivant peut valider
        return validator_level == (last_validation.level + 1)
    
    @classmethod
    def _create_notification(cls, user, gap, type, title, message, priority='normal'):
        """
        Crée une notification.
        """
        Notification.objects.create(
            user=user,
            gap=gap,
            type=type,
            title=title,
            message=message,
            priority=priority
        )
    
    @classmethod
    def _mark_validation_notifications_read(cls, gap, validator):
        """
        Marque comme lues les notifications de validation pour un écart et un validateur donné.
        """
        updated_count = Notification.objects.filter(
            user=validator,
            gap=gap,
            type='validation_request',
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        # Debug: log combien de notifications ont été mises à jour
        print(f"DEBUG: Marqué {updated_count} notifications comme lues pour {validator} sur écart {gap.gap_number}")
        
        # Marquer aussi toutes les notifications non lues de validation_request pour ce validateur
        # au cas où il y aurait un problème de correspondance
        additional_count = Notification.objects.filter(
            user=validator,
            type='validation_request',
            is_read=False,
            title__contains=gap.gap_number
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        print(f"DEBUG: Marqué {additional_count} notifications supplémentaires par numéro d'écart")