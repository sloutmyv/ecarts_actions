#!/usr/bin/env python3
"""
Script pour créer des données d'exemple.
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecarts_actions.settings')
django.setup()

from core.models import AuditSource, Department, Process, GapType

def main():
    # Créer des sources d'audit
    audit_sources = [
        {"code": "AI", "name": "Audit interne", "requires_process": True},
        {"code": "AC", "name": "Audit client", "requires_process": False},
        {"code": "IV", "name": "Inspection visuelle", "requires_process": False},
        {"code": "RC", "name": "Retour client", "requires_process": False},
    ]

    print("Création des sources d'audit...")
    for source_data in audit_sources:
        obj, created = AuditSource.objects.get_or_create(**source_data)
        if created:
            print(f"  - {obj.name} créé")
        else:
            print(f"  - {obj.name} existe déjà")

    # Créer des départements
    departments = [
        {"code": "PROD", "name": "Production"},
        {"code": "QUA", "name": "Qualité"},
        {"code": "LOG", "name": "Logistique"},
        {"code": "RH", "name": "Ressources Humaines"},
    ]

    print("\nCréation des départements...")
    for dept_data in departments:
        obj, created = Department.objects.get_or_create(**dept_data)
        if created:
            print(f"  - {obj.name} créé")
        else:
            print(f"  - {obj.name} existe déjà")

    # Créer des processus
    processes = [
        {"code": "PROC001", "name": "Gestion des commandes"},
        {"code": "PROC002", "name": "Contrôle qualité"},
        {"code": "PROC003", "name": "Formation du personnel"},
        {"code": "PROC004", "name": "Maintenance préventive"},
    ]

    print("\nCréation des processus...")
    for process_data in processes:
        obj, created = Process.objects.get_or_create(**process_data)
        if created:
            print(f"  - {obj.name} créé")
        else:
            print(f"  - {obj.name} existe déjà")

    # Créer des types d'écarts
    gap_types = [
        # Pour audit interne
        {"code": "AI001", "name": "Non-conformité documentaire", "audit_source": AuditSource.objects.get(code="AI")},
        {"code": "AI002", "name": "Non-respect des procédures", "audit_source": AuditSource.objects.get(code="AI")},
        {"code": "AI003", "name": "Formation insuffisante", "audit_source": AuditSource.objects.get(code="AI")},
        
        # Pour audit client
        {"code": "AC001", "name": "Produit non conforme", "audit_source": AuditSource.objects.get(code="AC")},
        {"code": "AC002", "name": "Délai non respecté", "audit_source": AuditSource.objects.get(code="AC")},
        {"code": "AC003", "name": "Service client défaillant", "audit_source": AuditSource.objects.get(code="AC")},
        
        # Pour inspection visuelle
        {"code": "IV001", "name": "Défaut d'aspect", "audit_source": AuditSource.objects.get(code="IV")},
        {"code": "IV002", "name": "Problème d'étiquetage", "audit_source": AuditSource.objects.get(code="IV")},
        
        # Pour retour client
        {"code": "RC001", "name": "Réclamation qualité", "audit_source": AuditSource.objects.get(code="RC")},
        {"code": "RC002", "name": "Problème de livraison", "audit_source": AuditSource.objects.get(code="RC")},
    ]

    print("\nCréation des types d'écarts...")
    for gap_type_data in gap_types:
        obj, created = GapType.objects.get_or_create(**gap_type_data)
        if created:
            print(f"  - {obj.name} créé")
        else:
            print(f"  - {obj.name} existe déjà")

    print("\nDonnées d'exemple créées avec succès!")

if __name__ == "__main__":
    main()