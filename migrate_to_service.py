#!/usr/bin/env python3
"""
Script pour migrer les données de Department vers Service.
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecarts_actions.settings')
django.setup()

from core.models import Service

def main():
    print("Migration vers Service...")
    
    # Comme nous n'avons pas encore de données GapReport avec Department,
    # nous allons juste créer quelques services d'exemple
    
    services_data = [
        {"code": "PROD", "nom": "Production"},
        {"code": "QUA", "nom": "Qualité"},
        {"code": "LOG", "nom": "Logistique"},
        {"code": "RH", "nom": "Ressources Humaines"},
        {"code": "MAINT", "nom": "Maintenance"},
        {"code": "COM", "nom": "Commercial"},
    ]
    
    print("Création des services d'exemple...")
    for service_data in services_data:
        obj, created = Service.objects.get_or_create(**service_data)
        if created:
            print(f"  - {obj.nom} créé")
        else:
            print(f"  - {obj.nom} existe déjà")
    
    print("\nMigration terminée avec succès!")

if __name__ == "__main__":
    main()