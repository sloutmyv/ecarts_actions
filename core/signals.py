"""
Signaux Django pour l'historique des modifications.
"""
import json
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from threading import local

from .models.gaps import GapReport, Gap, HistoriqueModification

User = get_user_model()

# Thread-local storage pour stocker l'utilisateur actuel et les données avant modification
_thread_locals = local()


def set_current_user(user):
    """
    Définit l'utilisateur actuel pour le thread.
    À appeler depuis les vues ou middlewares.
    """
    _thread_locals.user = user


def get_current_user():
    """
    Récupère l'utilisateur actuel du thread.
    """
    return getattr(_thread_locals, 'user', None)


def _serialize_model_instance(instance, for_json=False):
    """
    Sérialise une instance de modèle en dictionnaire.
    
    Args:
        instance: L'instance à sérialiser
        for_json: Si True, convertit les datetime en ISO format pour JSON
    """
    if not instance:
        return None
    
    data = {}
    for field in instance._meta.fields:
        field_name = field.name
        field_value = getattr(instance, field_name)
        
        # Convertir les objets complexes en représentations simples
        if hasattr(field_value, 'pk'):
            data[field_name] = {
                'id': field_value.pk,
                'str': str(field_value)
            }
        elif hasattr(field_value, 'isoformat'):  # datetime objects
            if for_json:
                # Pour le stockage JSON, convertir en ISO format
                data[field_name] = field_value.isoformat()
            else:
                # Pour la comparaison, conserver l'objet datetime
                data[field_name] = field_value
        else:
            data[field_name] = field_value
    
    return data


def _convert_data_for_json(data):
    """
    Convertit les données contenant des objets datetime en format JSON.
    """
    if not data:
        return None
    
    json_data = {}
    for field_name, field_value in data.items():
        if hasattr(field_value, 'isoformat'):  # datetime objects
            json_data[field_name] = field_value.isoformat()
        else:
            json_data[field_name] = field_value
    
    return json_data


def _get_field_changes(old_data, new_instance):
    """
    Compare les données anciennes avec la nouvelle instance et retourne les changements.
    """
    if not old_data:
        return {}
    
    changes = {}
    new_data = _serialize_model_instance(new_instance, for_json=False)
    
    for field_name, old_value in old_data.items():
        new_value = new_data.get(field_name)
        if old_value != new_value:
            changes[field_name] = {
                'avant': old_value,
                'apres': new_value
            }
    
    return changes


def _generate_change_description(changes, action, model_name, instance=None):
    """
    Génère une description lisible des changements.
    """
    if action == 'creation':
        # Cas spécial pour la création d'écarts et déclarations
        if instance:
            from .models.gaps import Gap, GapReport
            if isinstance(instance, Gap):
                return f"Création de l'événement {instance.gap_number}"
            elif isinstance(instance, GapReport):
                return f"Création de déclaration d'événement {instance.id}"
        return f"Création de {model_name.lower()}"
    elif action == 'suppression':
        # Cas spécial pour la suppression d'écarts et déclarations
        if instance:
            from .models.gaps import Gap, GapReport
            if isinstance(instance, Gap):
                return f"Suppression de l'événement {instance.gap_number}"
            elif isinstance(instance, GapReport):
                return f"Suppression de déclaration d'événement {instance.id}"
        return f"Suppression de {model_name.lower()}"
    elif not changes:
        return f"Modification de {model_name.lower()} (aucun changement détecté)"
    
    descriptions = []
    field_labels = {
        'description': 'description',
        'status': 'statut',
        'gap_type': 'type d\'écart',
        'audit_source': 'source d\'audit',
        'service': 'service',
        'process': 'processus',
        'location': 'lieu',
        'observation_date': 'date d\'observation',
        'source_reference': 'référence source',
    }
    
    for field_name, change in changes.items():
        if field_name in ['created_at', 'updated_at']:
            continue  # Ignorer les champs de timestamp
            
        field_label = field_labels.get(field_name, field_name)
        old_val = change['avant']
        new_val = change['apres']
        
        # Formater les valeurs pour l'affichage
        if isinstance(old_val, dict) and 'str' in old_val:
            old_val = old_val['str']
        elif hasattr(old_val, 'strftime'):  # datetime objects
            old_val = old_val.strftime('%d/%m/%Y %H:%M')
            
        if isinstance(new_val, dict) and 'str' in new_val:
            new_val = new_val['str']
        elif hasattr(new_val, 'strftime'):  # datetime objects
            new_val = new_val.strftime('%d/%m/%Y %H:%M')
            
        # Cas spécial pour les changements de statut des écarts
        if field_name == 'status' and action == 'changement_statut':
            # Importer Gap ici pour éviter les imports circulaires  
            from .models.gaps import Gap
            if instance and isinstance(instance, Gap):
                # Traduire les valeurs en français
                status_translations = {
                    'declared': 'Déclaré',
                    'cancelled': 'Annulé', 
                    'retained': 'Retenu',
                    'rejected': 'Non retenu',
                    'closed': 'Clos'
                }
                old_val_fr = status_translations.get(old_val, old_val)
                new_val_fr = status_translations.get(new_val, new_val)
                descriptions.append(f"Changement de statut de l'événement {instance.gap_number} de '{old_val_fr}' vers '{new_val_fr}'")
            else:
                descriptions.append(f"Changement de statut de '{old_val}' vers '{new_val}'")
        else:
            descriptions.append(f"{field_label}: '{old_val}' → '{new_val}'")
    
    # Pour les changements de statut d'écart, retourner directement la description
    if action == 'changement_statut':
        # Si on a une description personnalisée pour l'écart, l'utiliser directement
        if len(descriptions) == 1 and descriptions[0].startswith('Changement de statut de l\'événement'):
            return descriptions[0]
        # Sinon, utiliser le format générique
        elif len(descriptions) == 1:
            return descriptions[0]
    
    # Cas spécial pour les modifications d'écarts et déclarations
    if instance:
        from .models.gaps import Gap, GapReport
        if isinstance(instance, Gap):
            return f"Modification de l'événement {instance.gap_number} - " + ', '.join(descriptions)
        elif isinstance(instance, GapReport):
            return f"Modification de déclaration d'événement {instance.id} - " + ', '.join(descriptions)
    
    return f"Modification de {model_name.lower()} - " + ', '.join(descriptions)


@receiver(pre_save, sender=GapReport)
@receiver(pre_save, sender=Gap)
def store_pre_save_data(sender, instance, **kwargs):
    """
    Stocke les données avant modification pour comparaison.
    Optimisé pour réduire les requêtes en environnement concurrent.
    """
    if instance.pk:  # Modification d'un objet existant
        try:
            # Optimisation : utiliser only() pour récupérer seulement les champs nécessaires
            fields_to_track = []
            if sender == GapReport:
                fields_to_track = [
                    'audit_source', 'source_reference', 'service', 'process',
                    'location', 'observation_date', 'declared_by'
                ]
            elif sender == Gap:
                fields_to_track = [
                    'gap_type', 'description', 'status', 'gap_number'
                ]
            
            old_instance = sender.objects.only(*fields_to_track).get(pk=instance.pk)
            _thread_locals.__dict__[f'pre_save_{sender.__name__}_{instance.pk}'] = _serialize_model_instance(old_instance, for_json=False)
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=GapReport)
def log_gap_report_changes(sender, instance, created, **kwargs):
    """
    Enregistre les modifications des Déclarations d'évenements.
    """
    user = get_current_user()
    if not user:
        return  # Pas d'utilisateur défini, ignorer
    
    if created:
        # Création
        HistoriqueModification.enregistrer_modification(
            objet=instance,
            action='creation',
            utilisateur=user,
            description=_generate_change_description({}, 'creation', 'déclaration d\'événement', instance),
            donnees_apres=_serialize_model_instance(instance, for_json=True)
        )
    else:
        # Modification
        old_data = getattr(_thread_locals, f'pre_save_{sender.__name__}_{instance.pk}', None)
        changes = _get_field_changes(old_data, instance)
        
        if changes:  # Seulement si il y a des changements réels
            HistoriqueModification.enregistrer_modification(
                objet=instance,
                action='modification',
                utilisateur=user,
                description=_generate_change_description(changes, 'modification', 'déclaration d\'événement', instance),
                donnees_avant=_convert_data_for_json(old_data),
                donnees_apres=_serialize_model_instance(instance, for_json=True)
            )


@receiver(post_save, sender=Gap)
def log_gap_changes(sender, instance, created, **kwargs):
    """
    Enregistre les modifications des événements et déclenche les notifications de validation.
    """
    user = get_current_user()
    if not user:
        return  # Pas d'utilisateur défini, ignorer
    
    if created:
        # Création
        HistoriqueModification.enregistrer_modification(
            objet=instance,
            action='creation',
            utilisateur=user,
            description=_generate_change_description({}, 'creation', 'événement', instance),
            donnees_apres=_serialize_model_instance(instance, for_json=True)
        )
        
        # Si c'est un écart (is_gap=True) en statut déclaré, créer une notification de validation
        if instance.gap_type.is_gap and instance.status == 'declared':
            from .services.validation_service import ValidationService
            ValidationService.create_gap_notification(instance)
        
        # Créer une notification pour le déclarant sur la création de l'écart
        if hasattr(instance, 'gap_report') and instance.gap_report and instance.gap_report.declared_by != user:
            from .models.notifications import Notification
            Notification.objects.create(
                user=instance.gap_report.declared_by,
                gap=instance,
                type='gap_created',
                title=f"{instance.gap_number} - Événement créé",
                message=f"Votre événement {instance.gap_number} ({instance.gap_type.name}) a été créé avec succès.",
                priority='normal'
            )
        elif hasattr(instance, 'gap_report') and instance.gap_report and instance.gap_report.declared_by == user:
            # Auto-notification pour le créateur
            from .models.notifications import Notification
            Notification.objects.create(
                user=user,
                gap=instance,
                type='gap_created',
                title=f"{instance.gap_number} - Événement créé",
                message=f"Votre événement {instance.gap_number} ({instance.gap_type.name}) a été créé avec succès.",
                priority='normal'
            )
            
    else:
        # Modification
        old_data = getattr(_thread_locals, f'pre_save_{sender.__name__}_{instance.pk}', None)
        changes = _get_field_changes(old_data, instance)
        
        if changes:  # Seulement si il y a des changements réels
            # Vérifier si c'est un changement de statut spécifique
            action = 'modification'
            if 'status' in changes:
                action = 'changement_statut'
            
            HistoriqueModification.enregistrer_modification(
                objet=instance,
                action=action,
                utilisateur=user,
                description=_generate_change_description(changes, action, 'événement', instance),
                donnees_avant=_convert_data_for_json(old_data),
                donnees_apres=_serialize_model_instance(instance, for_json=True)
            )
            
            # Créer une notification pour le déclarant sur la modification de l'écart
            if hasattr(instance, 'gap_report') and instance.gap_report and instance.gap_report.declared_by:
                from .models.notifications import Notification
                
                # Déterminer le type de notification selon le changement
                if 'status' in changes:
                    old_status = changes['status']['avant']
                    new_status = changes['status']['apres']
                    
                    if new_status == 'retained':
                        notification_type = 'gap_retained'
                        title = f"Écart {instance.gap_number} retenu"
                        message = f"Votre événement {instance.gap_number} a été validé et retenu."
                    elif new_status == 'rejected':
                        notification_type = 'gap_rejected'
                        title = f"Écart {instance.gap_number} rejeté"
                        message = f"Votre événement {instance.gap_number} a été rejeté."
                    else:
                        notification_type = 'gap_modified'
                        title = f"Écart {instance.gap_number} modifié"
                        message = f"Le statut de votre écart {instance.gap_number} a été modifié : {old_status} → {new_status}."
                else:
                    notification_type = 'gap_modified'
                    title = f"Écart {instance.gap_number} modifié"
                    message = f"Votre événement {instance.gap_number} a été modifié."
                
                Notification.objects.create(
                    user=instance.gap_report.declared_by,
                    gap=instance,
                    type=notification_type,
                    title=title,
                    message=message,
                    priority='normal'
                )


@receiver(post_delete, sender=GapReport)
def log_gap_report_deletion(sender, instance, **kwargs):
    """
    Enregistre la suppression des Déclarations d'évenements.
    """
    user = get_current_user()
    if not user:
        return
    
    # Pour les suppressions, on crée une entrée spéciale car l'objet n'existe plus
    HistoriqueModification.objects.create(
        gap_report=None,  # L'objet est supprimé
        gap=None,
        action='suppression',
        objet_type='gap_report',
        objet_id=instance.id,
        objet_repr=str(instance),
        utilisateur=user,
        description=_generate_change_description({}, 'suppression', 'déclaration d\'événement', instance),
        donnees_avant=_serialize_model_instance(instance, for_json=True)
    )


@receiver(post_delete, sender=Gap)
def log_gap_deletion(sender, instance, **kwargs):
    """
    Enregistre la suppression des événements.
    """
    user = get_current_user()
    if not user:
        return
    
    # Pour les suppressions, on crée une entrée spéciale car l'objet n'existe plus
    HistoriqueModification.objects.create(
        gap_report=instance.gap_report,  # On garde la référence à la déclaration
        gap=None,  # L'événement est supprimé
        action='suppression',
        objet_type='gap',
        objet_id=instance.id,
        objet_repr=str(instance),
        utilisateur=user,
        description=_generate_change_description({}, 'suppression', 'événement', instance),
        donnees_avant=_serialize_model_instance(instance, for_json=True)
    )
    
    # Créer une notification pour le déclarant sur la suppression de l'écart
    if hasattr(instance, 'gap_report') and instance.gap_report and instance.gap_report.declared_by:
        from .models.notifications import Notification
        
        Notification.objects.create(
            user=instance.gap_report.declared_by,
            gap=None,  # L'événement est supprimé, pas de référence
            type='gap_deleted',
            title=f"{instance.gap_number} - Événement supprimé",
            message=f"Votre événement {instance.gap_number} ({instance.gap_type.name}) a été supprimé.",
            priority='normal'
        )