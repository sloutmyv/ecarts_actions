#!/usr/bin/env python3
"""
Script pour assigner des services aux utilisateurs existants.
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecarts_actions.settings')
django.setup()

from core.models import User, Service

def main():
    print("Attribution des services aux utilisateurs...")
    
    # Récupérer les services existants
    commercial = Service.objects.filter(code="COM").first()
    dg = Service.objects.filter(code="DG").first()
    
    if not commercial or not dg:
        print("Erreur: Services COM ou DG non trouvés")
        return
    
    # Assigner des services aux utilisateurs
    users = User.objects.all()
    
    for i, user in enumerate(users):
        if not user.service:  # Seulement si l'utilisateur n'a pas déjà un service
            # Alterner entre Commercial et Direction Générale
            if i % 2 == 0:
                user.service = commercial
                print(f"  - {user.matricule} ({user.get_full_name()}) → {commercial.nom}")
            else:
                user.service = dg
                print(f"  - {user.matricule} ({user.get_full_name()}) → {dg.nom}")
            
            user.save()
        else:
            print(f"  - {user.matricule} ({user.get_full_name()}) a déjà le service: {user.service.nom}")
    
    print("\nAttribution terminée avec succès!")

if __name__ == "__main__":
    main()