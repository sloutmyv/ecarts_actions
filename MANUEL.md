# EcartsActions - Manuel Utilisateur

## 📋 Table des matières

- [Introduction](#introduction)
- [Connexion et navigation](#connexion-et-navigation)
- [Gestion des Services](#gestion-des-services)
- [Import/Export des données](#importexport-des-données)
- [Interface d'administration Django](#interface-dadministration-django)
- [Résolution des problèmes](#résolution-des-problèmes)
- [Glossaire](#glossaire)

## 📖 Introduction

### Qu'est-ce qu'EcartsActions ?

EcartsActions est une application de **gestion d'écarts et d'actions** qui permet de :
- Gérer une structure organisationnelle hiérarchique (services/départements)
- Suivre et traiter les écarts/non-conformités (fonctionnalité à venir)
- Planifier et suivre les actions correctives (fonctionnalité à venir)

### Public cible

Ce manuel s'adresse aux :
- **Administrateurs** : Responsables de la configuration et de la maintenance
- **Gestionnaires** : Utilisateurs gérant les services et l'organisation
- **Utilisateurs finaux** : Personnels utilisant l'application pour consulter et saisir des données

## 🔐 Connexion et navigation

### Se connecter à l'application

1. **Accéder à l'application**
   - Ouvrez votre navigateur web
   - Rendez-vous à l'adresse fournie par votre administrateur
   - Exemple : `http://votre-serveur.com:8000/`

2. **Page de connexion**
   - Cliquez sur le lien "Administration" dans la navigation
   - Saisissez vos identifiants (nom d'utilisateur et mot de passe)
   - Cliquez sur "Se connecter"

### Interface principale

Une fois connecté, vous accédez à l'interface principale avec :

#### Barre de navigation supérieure
- **Écarts & Actions** : Nom de l'application (lien vers l'accueil)
- **Tableau de bord** : Vue d'ensemble des statistiques
- **Écarts** : Gestion des non-conformités (à venir)
- **Plan d'actions** : Suivi des actions correctives (à venir)
- **Administration** : Menu déroulant avec les options de gestion

#### Menu Administration
- **Gestion des Services** : Interface principale pour les services
- **Administration Django** : Interface d'administration avancée

#### Zone utilisateur (coin supérieur droit)
- **Avatar** : Initiales de l'utilisateur connecté
- **Nom** : Nom complet de l'utilisateur
- **Déconnexion** : Bouton de déconnexion sécurisée

## 🏢 Gestion des Services

### Vue d'ensemble des Services

Les **Services** représentent l'organisation hiérarchique de votre entreprise :
- **Services racines** : Directions principales
- **Sous-services** : Départements et sous-départements
- **Hiérarchie illimitée** : Autant de niveaux que nécessaire

### Accéder à la gestion des Services

1. Dans la barre de navigation, cliquez sur **Administration**
2. Sélectionnez **Gestion des Services**
3. Vous arrivez sur la page de liste des services

### Interface de liste des Services

#### Affichage hiérarchique
- **Structure en arbre** : Les services sont affichés avec leur hiérarchie
- **Indicateurs visuels** : Lignes et icônes pour montrer les niveaux
- **Dropdowns** : Boutons fléchés pour plier/déplier les niveaux

#### Informations affichées pour chaque service
- **Icône** : 🏢 pour les services racines, 👥 pour les sous-services
- **Nom du service** : Nom complet du service
- **Code** : Code d'identification unique (ex: DG, DRH, COMPTA)
- **Nombre de sous-services** : Compteur des services enfants
- **Date de création** : Date de création du service

#### Actions disponibles
- **✏️ Modifier** : Bouton bleu pour éditer le service
- **🗑️ Supprimer** : Bouton rouge pour supprimer le service

### Créer un nouveau Service

1. **Accéder au formulaire**
   - Cliquez sur le bouton **"Nouveau Service"** (coin supérieur droit)
   - Une fenêtre modale s'ouvre

2. **Remplir le formulaire**
   - **Nom du service** : Nom complet (ex: "Direction des Ressources Humaines")
   - **Code du service** : Code unique court (ex: "DRH")
   - **Service parent** : Sélectionner le service parent dans la liste déroulante
     - Laisser vide pour créer un service racine

3. **Valider la création**
   - Cliquez sur **"Créer"**
   - Le service apparaît immédiatement dans la liste
   - Un message de confirmation s'affiche

### Modifier un Service existant

1. **Accéder au formulaire**
   - Cliquez sur l'icône **✏️** à droite du service à modifier
   - Une fenêtre modale s'ouvre avec les données actuelles

2. **Modifier les informations**
   - Changez le nom, le code ou le service parent
   - **Attention** : Modifier le service parent change la hiérarchie

3. **Valider les modifications**
   - Cliquez sur **"Modifier"**
   - Les changements sont appliqués immédiatement
   - Un message de confirmation s'affiche

### Supprimer un Service

1. **Conditions de suppression**
   - ⚠️ Un service avec des sous-services ne peut pas être supprimé
   - Il faut d'abord supprimer ou déplacer tous les sous-services

2. **Processus de suppression**
   - Cliquez sur l'icône **🗑️** à droite du service
   - Une confirmation est demandée
   - Confirmez la suppression
   - Le service disparaît de la liste

### Bonnes pratiques

#### Nomenclature des codes
- **Services racines** : 2-3 lettres (DG, DRH, DF, DT)
- **Sous-services** : 3-6 lettres explicites (COMPTA, REC, FORM)
- **Cohérence** : Utilisez une logique commune dans votre organisation

#### Organisation hiérarchique
```
✅ Structure recommandée :
Direction Générale (DG)
├── Direction des Ressources Humaines (DRH)
│   ├── Service Recrutement (REC)
│   └── Service Formation (FORM)
└── Direction Financière (DF)
    ├── Comptabilité (COMPTA)
    └── Contrôle de Gestion (CG)
```

## 📥📤 Import/Export des données

### Export des Services en JSON

L'export permet de sauvegarder vos données organisationnelles au format JSON.

#### Processus d'export
1. **Accéder à l'export**
   - Allez dans **Administration Django** → **Services**
   - Cliquez sur **"Exporter en JSON"** (bouton vert)

2. **Téléchargement automatique**
   - Le fichier se télécharge automatiquement
   - Nom du fichier : `Service_YYMMDD.json` (ex: `Service_241028.json`)

3. **Contenu du fichier**
   - Tous les services avec leur hiérarchie
   - Métadonnées : date d'export, nombre d'enregistrements
   - Données complètes : nom, code, relations parent-enfant

### Import des Services depuis JSON

L'import permet de restaurer ou de synchroniser vos données depuis un fichier JSON.

⚠️ **ATTENTION - Import destructif** : Cette opération remplace **INTÉGRALEMENT** la base de données existante.

#### Préparer le fichier d'import
- **Format requis** : JSON avec structure spécifique
- **Source** : Fichier exporté depuis EcartsActions ou compatible
- **Sauvegarde obligatoire** : Effectuez toujours un export avant l'import

#### Processus d'import
1. **Accéder à l'import**
   - Allez dans **Administration Django** → **Services**
   - Cliquez sur **"Importer depuis JSON"** (bouton bleu)

2. **⚠️ Avertissements importants**
   - **Import destructif** : TOUS les services existants seront SUPPRIMÉS
   - **Remplacement total** : La base de données sera ENTIÈREMENT REMPLACÉE
   - **Action irréversible** : Il est IMPOSSIBLE d'annuler cette opération
   - **Sauvegarde obligatoire** : Exportez vos données avant l'import

3. **Sélectionner le fichier**
   - Cliquez sur **"📄 Fichier JSON à importer"**
   - Sélectionnez votre fichier `.json`
   - Vérifiez que le fichier correspond à la structure attendue
   - Cliquez sur **"🚀 Lancer l'import"**

4. **Traitement automatique en deux phases**
   
   **Phase 1 - Suppression :**
   - Suppression de TOUS les services existants
   - Nettoyage complet de la base de données
   
   **Phase 2 - Import en deux passes :**
   - **Première passe** : Création de tous les services sans relations parent-enfant
   - **Deuxième passe** : Établissement des relations hiérarchiques
   - **Respect de l'ordre** : Les dépendances sont automatiquement résolues
   - **Mapping des ID** : Les anciens ID sont mappés vers les nouveaux

5. **Rapport d'import**
   - Nombre de services supprimés
   - Nombre de services importés
   - Erreurs éventuelles détaillées
   - Confirmation de la réussite ou échec

#### Gestion des dépendances hiérarchiques

**Problématique** : Les services étant liés entre eux par des relations parent-enfant, l'ordre d'import est crucial pour éviter d'endommager la base de données.

**Solution automatique** :
1. **Tri automatique** : Les services sont triés (parents avant enfants)
2. **Import en deux passes** :
   - **Passe 1** : Création de tous les services sans parent
   - **Passe 2** : Attribution des relations parent-enfant
3. **Mapping des ID** : Les anciens ID sont conservés en mémoire pour reconstituer les liens
4. **Transaction atomique** : En cas d'erreur, AUCUNE modification n'est appliquée

**Exemple d'ordre de traitement** :
```
❌ Ordre problématique (échouerait) :
- Service Comptabilité (parent: Direction Financière) → parent n'existe pas encore
- Direction Financière (parent: null) → créé après son enfant

✅ Ordre automatique (réussi) :
- Direction Financière (parent: null) → créé en premier
- Service Comptabilité (parent: Direction Financière) → parent existe déjà
```

#### Gestion des erreurs et rollback
- **Transaction atomique** : Tous les changements sont dans une transaction unique
- **Rollback automatique** : En cas d'erreur, la base de données est restaurée à son état initial
- **Validation préalable** : Le fichier JSON est validé avant le traitement
- **Messages d'erreur détaillés** : Chaque erreur est documentée avec le service concerné

### Format de fichier JSON

#### Structure du fichier d'export
```json
{
  "model": "Service",
  "export_date": "2024-10-28T14:30:00",
  "total_records": 3,
  "data": [
    {
      "id": 1,
      "nom": "Direction Générale",
      "code": "DG",
      "parent_id": null,
      "parent_code": null,
      "created_at": "2024-10-28T10:00:00",
      "updated_at": "2024-10-28T10:00:00"
    },
    {
      "id": 2,
      "nom": "Direction des Ressources Humaines",
      "code": "DRH",
      "parent_id": 1,
      "parent_code": "DG",
      "created_at": "2024-10-28T10:15:00",
      "updated_at": "2024-10-28T10:15:00"
    }
  ]
}
```

## ⚙️ Interface d'administration Django

### Accès à l'administration Django

L'interface Django Admin offre des fonctionnalités avancées pour les administrateurs.

#### Se connecter
1. Cliquez sur **Administration** → **Administration Django**
2. Saisissez vos identifiants administrateur
3. Accédez au panneau d'administration

#### Fonctionnalités disponibles

##### Section "1. Services"
- **Liste des services** : Vue tableau avec filtres et recherche
- **Ajout/Modification** : Formulaires détaillés
- **Actions en masse** : Opérations sur plusieurs services
- **Import/Export** : Boutons d'import/export JSON

##### Fonctionnalités avancées
- **Filtres** : Par service parent, date de création
- **Recherche** : Par nom ou code de service
- **Tri** : Par colonnes (nom, code, date)
- **Pagination** : Navigation dans les listes longues

### Gestion des utilisateurs (Administrateurs uniquement)

#### Accès à la gestion des utilisateurs
- Section **"Authentification et autorisation"**
- **Utilisateurs** : Gestion des comptes utilisateurs
- **Groupes** : Organisation par rôles et permissions

#### Créer un nouvel utilisateur
1. Cliquez sur **"Ajouter"** dans la section Utilisateurs
2. Remplissez les informations obligatoires :
   - Nom d'utilisateur
   - Mot de passe
3. Définissez les permissions :
   - **Statut de l'équipe** : Accès à l'admin
   - **Statut de superutilisateur** : Tous les droits
   - **Permissions spécifiques** : Droits granulaires

## 🔧 Résolution des problèmes

### Problèmes fréquents

#### Impossible de supprimer un service
**Symptôme** : Message d'erreur lors de la suppression
**Cause** : Le service contient des sous-services
**Solution** :
1. Déplacez ou supprimez d'abord tous les sous-services
2. Recommencez la suppression du service parent

#### Erreur "Code déjà existant"
**Symptôme** : Impossible de créer/modifier un service
**Cause** : Le code saisi existe déjà
**Solution** :
1. Vérifiez l'unicité du code
2. Choisissez un code différent
3. Ou modifiez le service existant

#### Import JSON échoue
**Symptôme** : Erreur lors de l'import
**Causes possibles** :
- Format JSON invalide
- Structure de données incorrecte
- Dépendances circulaires

**Solutions** :
1. Vérifiez la validité du JSON (outil en ligne)
2. Utilisez uniquement des fichiers exportés depuis EcartsActions
3. Contactez votre administrateur

#### Page ne se charge pas
**Symptôme** : Erreur 404 ou 500
**Solutions** :
1. Actualisez la page (F5)
2. Vérifiez votre connexion internet
3. Contactez votre administrateur système

### Support technique

#### Informations à fournir en cas de problème
- **URL de la page** où le problème survient
- **Message d'erreur** exact (capture d'écran)
- **Actions effectuées** avant le problème
- **Navigateur utilisé** (Chrome, Firefox, etc.)
- **Heure approximative** du problème

#### Contact support
Contactez votre administrateur système en fournissant toutes les informations ci-dessus.

## 📚 Glossaire

### Termes techniques

**Service**
: Unité organisationnelle représentant un département, une direction ou un service de l'entreprise.

**Service racine**
: Service situé au plus haut niveau hiérarchique, sans service parent.

**Sous-service**
: Service ayant un service parent dans la hiérarchie organisationnelle.

**Code de service**
: Identifiant unique court (2-6 caractères) permettant d'identifier rapidement un service.

**Hiérarchie**
: Structure arborescente des services montrant les relations parent-enfant.

**Import/Export JSON**
: Fonctionnalité de sauvegarde et restauration des données au format JSON.

### Termes métier

**Écart**
: Non-conformité ou dysfonctionnement identifié dans un processus (fonctionnalité à venir).

**Action corrective**
: Mesure prise pour corriger un écart identifié (fonctionnalité à venir).

**Plan d'actions**
: Ensemble coordonné d'actions correctives avec échéances et responsables (fonctionnalité à venir).

### Conventions d'interface

**Modal/Fenêtre modale**
: Fenêtre qui s'ouvre par-dessus l'interface principale pour afficher un formulaire.

**Dropdown**
: Menu déroulant permettant de sélectionner une option parmi plusieurs.

**HTMX**
: Technologie permettant les interactions sans rechargement de page.

**Alpine.js**
: Framework JavaScript léger pour l'interactivité côté client.

---

**📝 Note** : Ce manuel est mis à jour régulièrement. La version la plus récente est disponible dans le repository du projet.

**🔄 Dernière mise à jour** : Janvier 2025