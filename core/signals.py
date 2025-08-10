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


def _generate_change_description(changes, action, model_name):
    """
    Génère une description lisible des changements.
    """
    if action == 'creation':
        return f"Création de {model_name.lower()}"
    elif action == 'suppression':
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
            
        descriptions.append(f"{field_label}: '{old_val}' → '{new_val}'")
    
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
            description=_generate_change_description({}, 'creation', 'déclaration d\'événement'),
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
                description=_generate_change_description(changes, 'modification', 'déclaration d\'événement'),
                donnees_avant=_convert_data_for_json(old_data),
                donnees_apres=_serialize_model_instance(instance, for_json=True)
            )


@receiver(post_save, sender=Gap)
def log_gap_changes(sender, instance, created, **kwargs):
    """
    Enregistre les modifications des événements.
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
            description=_generate_change_description({}, 'creation', 'événement'),
            donnees_apres=_serialize_model_instance(instance, for_json=True)
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
                description=_generate_change_description(changes, action, 'événement'),
                donnees_avant=_convert_data_for_json(old_data),
                donnees_apres=_serialize_model_instance(instance, for_json=True)
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
        description=_generate_change_description({}, 'suppression', 'déclaration d\'événement'),
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
        gap=None,  # L'écart est supprimé
        action='suppression',
        objet_type='gap',
        objet_id=instance.id,
        objet_repr=str(instance),
        utilisateur=user,
        description=_generate_change_description({}, 'suppression', 'événement'),
        donnees_avant=_serialize_model_instance(instance, for_json=True)
    )