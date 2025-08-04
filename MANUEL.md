# EcartsActions - Manuel Utilisateur

## 📋 Table des matières

- [Introduction](#introduction)
- [Connexion et authentification](#connexion-et-authentification)
- [Navigation et droits d'accès](#navigation-et-droits-dacces)
- [Gestion des Services](#gestion-des-services)
- [Gestion des Utilisateurs](#gestion-des-utilisateurs)
- [Gestion des Écarts](#gestion-des-écarts)
- [Import/Export des données](#importexport-des-données)
- [Interface d'administration Django](#interface-dadministration-django)
- [Résolution des problèmes](#résolution-des-problèmes)
- [Glossaire](#glossaire)

## 📖 Introduction

### Qu'est-ce qu'EcartsActions ?

EcartsActions est une application de **gestion d'écarts et d'actions** qui permet de :
- Gérer une structure organisationnelle hiérarchique (services/départements)
- Gérer les utilisateurs avec un système de droits à 3 niveaux
- Authentification sécurisée par matricule avec changement de mot de passe obligatoire
- Déclarer et suivre les écarts/non-conformités avec un système complet de gestion
- Planifier et suivre les actions correctives (fonctionnalité à venir)

### Public cible

Ce manuel s'adresse aux :
- **Super Administrateurs** : Accès complet à toutes les fonctionnalités (y compris Admin Django)
- **Administrateurs** : Gestion des services et utilisateurs (sans Admin Django)
- **Utilisateurs** : Accès aux fonctionnalités principales (Dashboard, Écarts, Actions)
- **Gestionnaires IT** : Responsables de la configuration technique et maintenance

## 🔐 Connexion et authentification

### Se connecter à l'application

1. **Accéder à l'application**
   - Ouvrez votre navigateur web
   - Rendez-vous à l'adresse fournie par votre administrateur
   - Exemple : `http://votre-serveur.com:8000/`

2. **Page de connexion personnalisée**
   - La page de connexion affiche le logo ENERCAL
   - **Matricule** : Saisissez votre matricule (format : Lettre + 4 chiffres, ex: A1234)
   - **Mot de passe** : Saisissez votre mot de passe
   - **Mot de passe par défaut** : `azerty` (vous devrez le changer à la première connexion)
   - Cliquez sur **"Se connecter"**

3. **Première connexion - Changement de mot de passe obligatoire**
   - Si c'est votre première connexion, vous serez automatiquement redirigé
   - Page de changement de mot de passe avec logo ENERCAL
   - **Mot de passe actuel** : Saisissez `azerty`
   - **Nouveau mot de passe** : Choisissez un mot de passe sécurisé (min. 8 caractères)
   - **Confirmer** : Ressaisissez le nouveau mot de passe
   - Cliquez sur **"Changer le mot de passe"**
   - Vous serez automatiquement redirigé vers le tableau de bord

### Déconnexion

- Cliquez sur le bouton **"Déconnexion"** dans la barre de navigation (coin supérieur droit)
- Vous serez redirigé vers la page de connexion
- Votre session sera complètement fermée pour la sécurité

## 🔒 Navigation et droits d'accès

### Système de droits à 3 niveaux

EcartsActions utilise un système de droits hiérarchique qui détermine l'accès aux fonctionnalités :

#### 🏆 Super Administrateur (SA)
**Accès complet** - Toutes les fonctionnalités disponibles
- ✅ **Navigation** : Tableau de bord, Écarts, Plan d'actions
- ✅ **Administration** : Menu Administration visible
  - ✅ Gestion des Services
  - ✅ Gestion des Utilisateurs  
  - ✅ Administration Django
- 🎯 **Utilisation** : Administrateurs système, Directeurs IT

#### 👨‍💼 Administrateur (AD)
**Accès administratif** - Gestion sans accès technique
- ✅ **Navigation** : Tableau de bord, Écarts, Plan d'actions
- ✅ **Administration** : Menu Administration visible
  - ✅ Gestion des Services
  - ✅ Gestion des Utilisateurs
  - ❌ Administration Django (masquée)
- 🎯 **Utilisation** : Responsables RH, Managers, Responsables qualité

#### 👤 Utilisateur (US)
**Accès standard** - Utilisation quotidienne
- ✅ **Navigation** : Tableau de bord, Écarts, Plan d'actions
- ❌ **Administration** : Menu Administration complètement masqué
- 🎯 **Utilisation** : Employés, Consultants, Utilisateurs finaux

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
- **Tri alphabétique automatique** : Services et sous-services triés par nom à tous les niveaux
- **Indicateurs visuels** : Lignes et icônes pour montrer les niveaux
- **Dropdowns** : Boutons fléchés pour plier/déplier les niveaux

#### Informations affichées pour chaque service
- **Icône** : 🏢 pour les services racines, 👥 pour les sous-services
- **Nom du service** : Nom complet du service
- **Code** : Code d'identification unique (ex: DG, DRH, COMPTA)
- **Nombre total de sous-services** : Compteur récursif incluant tous les niveaux de descendants
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

1. **Système de confirmation par modales**
   - Un nouveau système de confirmation sécurisé a été mis en place
   - Toutes les suppressions utilisent des modales de couleur orange pastel
   - Messages d'avertissement clairs et informatifs

2. **Processus de suppression**
   - Cliquez sur l'icône **🗑️** à droite du service
   - **Modal de confirmation** s'affiche avec fond orange pastel
   - **Trois scénarios possibles** :

   **🟢 Service sans dépendances**
   - Modal simple : "Êtes-vous sûr de vouloir supprimer ce service ?"
   - Cliquez sur **"Confirmer la suppression"** (rouge) ou **"Annuler"** (gris)

   **🟡 Service avec utilisateurs liés**
   - Modal d'avertissement : "Ce service est lié à X utilisateur(s)"
   - Message explicatif : "En le supprimant, vous allez retirer l'affectation des utilisateurs"
   - Cliquez sur **"Confirmer la suppression"** (rouge) ou **"Annuler"** (gris)

   **🔴 Service avec sous-services** 
   - Modal d'erreur : "Impossible de supprimer ce service"
   - Explication : "Ce service contient des sous-services"
   - Action requise : Supprimer d'abord tous les sous-services
   - Seul bouton **"Fermer"** disponible

3. **Finalisation**
   - Si confirmé, le service disparaît de la liste
   - Les utilisateurs liés sont automatiquement désaffectés

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

## 👤 Gestion des Utilisateurs

**Accès requis** : Super Administrateur ou Administrateur uniquement

### Vue d'ensemble des Utilisateurs

La gestion des utilisateurs permet de :
- **Créer et gérer** les comptes utilisateurs
- **Définir les niveaux de droits** (3 niveaux disponibles)
- **Associer** les utilisateurs aux services
- **Réinitialiser** les mots de passe
- **Gérer** les premières connexions

### Accéder à la gestion des Utilisateurs

1. Dans la barre de navigation, cliquez sur **Administration**
2. Sélectionnez **Gestion des Utilisateurs**
3. Vous arrivez sur la page de liste des utilisateurs

### Interface de liste des Utilisateurs

#### Informations affichées pour chaque utilisateur
- **Avatar** : Initiales (Prénom + Nom)
- **Nom complet** : Prénom et Nom de l'utilisateur  
- **Matricule** : Identifiant unique (ex: A1234)
- **Niveau de droits** : Badge coloré indiquant le niveau
  - 🔴 **Super Administrateur** : Badge rouge
  - 🔵 **Administrateur** : Badge bleu  
  - 🟢 **Utilisateur** : Badge vert
- **Service** : Service d'affectation (si assigné)
- **Email** : Adresse email (si renseignée)
- **Statut** : Indication si changement de mot de passe requis

#### Actions disponibles par utilisateur
- **👁️ Voir** : Consulter les détails de l'utilisateur (bouton indigo)
- **✏️ Modifier** : Éditer les informations (bouton bleu)
- **🔑 Réinitialiser** : Remettre le mot de passe à `azerty` (bouton orange)
- **🗑️ Supprimer** : Supprimer l'utilisateur (bouton rouge)
  - ⚠️ **Restriction** : Impossible de supprimer son propre compte

### Créer un nouvel Utilisateur

1. **Accéder au formulaire**
   - Cliquez sur le bouton **"Nouvel Utilisateur"** (coin supérieur droit)
   - Une fenêtre modale s'ouvre

2. **Remplir le formulaire**
   - **Nom** : Nom de famille de l'utilisateur
   - **Prénom** : Prénom de l'utilisateur
   - **Matricule** : Format obligatoire `[A-Z][0-9]{4}` (ex: A1234)
     - 1 lettre majuscule suivie de 4 chiffres
     - Doit être unique dans le système
   - **Email** : Adresse email (optionnel)
   - **Droits** : Sélectionner le niveau d'accès
     - Super Administrateur (SA)
     - Administrateur (AD) 
     - Utilisateur (US)
   - **Service** : Associer à un service existant (optionnel)

3. **Validation automatique**
   - **Mot de passe par défaut** : `azerty` (assigné automatiquement)
   - **Changement obligatoire** : L'utilisateur devra changer son mot de passe à la première connexion
   - **Validation matricule** : Vérification automatique du format

4. **Finaliser la création**
   - Cliquez sur **"Créer"**
   - L'utilisateur apparaît dans la liste
   - Un message de confirmation s'affiche

### Modifier un Utilisateur existant

1. **Accéder au formulaire**
   - Cliquez sur l'icône **✏️** à droite de l'utilisateur à modifier
   - Une fenêtre modale s'ouvre avec les données actuelles

2. **Modifier les informations**
   - Changez les informations nécessaires
   - **Attention** : Modifier les droits change immédiatement les accès
   - **Matricule** : Peut être modifié si nécessaire (doit rester unique)

3. **Valider les modifications**
   - Cliquez sur **"Modifier"**
   - Les changements sont appliqués immédiatement
   - L'utilisateur verra ses accès mis à jour à sa prochaine connexion

### Réinitialiser un mot de passe

1. **Processus de réinitialisation**
   - Cliquez sur l'icône **🔑** à droite de l'utilisateur
   - Une confirmation est demandée
   - Confirmez la réinitialisation

2. **Effet de la réinitialisation**
   - **Nouveau mot de passe** : `azerty`
   - **Changement obligatoire** : L'utilisateur devra changer son mot de passe à la prochaine connexion
   - **Session active** : Si l'utilisateur est connecté, il sera déconnecté automatiquement

### Supprimer un Utilisateur

1. **Conditions de suppression**
   - ✅ Peut supprimer tout utilisateur sauf soi-même
   - ❌ Impossible de supprimer son propre compte (protection)

2. **Système de confirmation par modale**
   - Nouveau système de confirmation sécurisé identique aux services
   - Modal de couleur orange pastel pour une expérience unifiée

3. **Processus de suppression**
   - Cliquez sur l'icône **🗑️** à droite de l'utilisateur
   - **Modal de confirmation** s'affiche avec fond orange pastel
   - Message : "Êtes-vous sûr de vouloir supprimer cet utilisateur ?"
   - Nom complet de l'utilisateur affiché pour confirmation
   - Cliquez sur **"Confirmer la suppression"** (rouge) ou **"Annuler"** (gris)

4. **Finalisation**
   - Si confirmé, l'utilisateur disparaît de la liste
   - L'utilisateur ne peut plus se connecter à l'application

### Bonnes pratiques de gestion des utilisateurs

#### Attribution des droits
- **Super Administrateur** : Réservé aux administrateurs système uniquement
- **Administrateur** : Pour les responsables RH, managers, responsables qualité
- **Utilisateur** : Pour tous les autres employés

#### Gestion des matricules
- **Format strict** : Respecter [A-Z][0-9]{4} (ex: A1234, B5678, Z9999)
- **Unicité** : Chaque matricule doit être unique dans l'organisation
- **Logique métier** : Utiliser une logique cohérente (ex: première lettre = service)

#### Sécurité
- **Réinitialisation** : Réinitialiser les mots de passe en cas de compromission
- **Suppression** : Supprimer immédiatement les comptes des employés qui quittent l'entreprise
- **Audit** : Vérifier régulièrement les droits attribués

### Import/Export des Utilisateurs

**Accès requis** : Super Administrateur uniquement

#### Export des Utilisateurs

La fonctionnalité d'export permet de sauvegarder la liste des utilisateurs au format JSON.

##### Processus d'export
1. **Accéder à l'export**
   - Allez dans **Administration Django** → **Utilisateurs**
   - Cliquez sur **"Exporter en JSON"** (bouton vert)

2. **Téléchargement automatique**
   - Le fichier se télécharge automatiquement
   - Nom du fichier : `Users_YYMMDD.json` (ex: `Users_250801.json`)

3. **Contenu du fichier**
   - Tous les utilisateurs avec leurs informations complètes
   - Métadonnées : date d'export, nombre d'enregistrements
   - Données complètes : matricule, nom, droits, service associé

##### Utilisation de l'export
- **Sauvegarde** : Conservation de la liste des utilisateurs
- **Audit** : Analyse des droits et affectations
- **Migration** : Transfert vers un autre système (avec adaptation)

⚠️ **Attention sécurité** : Le fichier d'export ne contient pas les mots de passe pour des raisons de sécurité.

#### Import des Utilisateurs

L'import permet de restaurer ou de synchroniser vos utilisateurs depuis un fichier JSON.

⚠️ **ATTENTION - Import destructif** : Cette opération supprime **TOUS** les utilisateurs existants (sauf l'utilisateur actuel).

##### Préparer le fichier d'import
- **Format requis** : JSON avec structure spécifique
- **Source** : Fichier exporté depuis EcartsActions ou compatible
- **Sauvegarde obligatoire** : Effectuez toujours un export avant l'import

##### Processus d'import
1. **Accéder à l'import**
   - Allez dans **Administration Django** → **Utilisateurs**
   - Cliquez sur **"Importer depuis JSON"** (bouton bleu)

2. **⚠️ Avertissements importants**
   - **Import destructif** : TOUS les utilisateurs existants seront SUPPRIMÉS (sauf vous-même)
   - **Remplacement total** : La base sera ENTIÈREMENT REMPLACÉE par le contenu du fichier JSON
   - **Action irréversible** : Il est IMPOSSIBLE d'annuler cette opération
   - **Sauvegarde obligatoire** : Exportez vos données avant l'import
   - **Protection administrateur** : Votre compte actuel sera préservé

3. **Sélectionner le fichier**
   - Cliquez sur **"📄 Fichier JSON à importer"**
   - Sélectionnez votre fichier `.json`
   - Vérifiez que le fichier correspond à la structure attendue
   - Cliquez sur **"🚀 Lancer l'import"**

4. **Traitement automatique**
   - **Suppression sécurisée** : Suppression de tous les utilisateurs sauf l'administrateur actuel
   - **Import des utilisateurs** : Création des nouveaux utilisateurs depuis le JSON
   - **Réinitialisation des mots de passe** : Tous les utilisateurs importés reçoivent le mot de passe "azerty"
   - **Changement obligatoire** : Tous devront changer leur mot de passe à la première connexion
   - **Association des services** : Les services sont automatiquement liés par code

5. **Rapport d'import**
   - Nombre d'utilisateurs supprimés
   - Nombre d'utilisateurs importés
   - Erreurs éventuelles détaillées
   - Confirmation de la réussite ou échec

##### Sécurités de l'import
- **Transaction atomique** : En cas d'erreur, AUCUNE modification n'est appliquée
- **Validation du fichier** : Format JSON et structure vérifiés avant traitement
- **Protection administrateur** : L'utilisateur effectuant l'import ne sera jamais supprimé
- **Mots de passe sécurisés** : Réinitialisation forcée avec changement obligatoire

## ⚠️ Gestion des Écarts

### Vue d'ensemble de la gestion des écarts

La gestion des écarts permet de déclarer, suivre et traiter les non-conformités qualité dans votre organisation. Le système offre une approche structurée pour identifier et résoudre les problèmes.

### Accéder à la gestion des écarts

1. **Naviguer vers les écarts**
   - Dans le menu principal, cliquez sur **"Écarts"**
   - Vous verrez deux options :
     - 📝 **"Déclarer un écart"** : Créer une nouvelle déclaration
     - 📋 **"Liste des écarts"** : Consulter tous les écarts existants

### Déclarer un nouvel écart

#### Étape 1 : Accès à la déclaration
- Cliquez sur **"Déclarer un écart"** dans le menu ou sur la page de liste
- Une modale moderne s'ouvre avec le formulaire de déclaration structuré en sections

#### Étape 2 : Section 🔵 "QUI ?" - Personnes impliquées
La déclaration commence par identifier les personnes présentes lors de l'observation :

**Déclarant (vous)**
- Affiché automatiquement à droite
- Votre nom, prénom et matricule
- Non modifiable (vous êtes toujours le déclarant)

**Autres personnes présentes** (optionnel)
- Bouton ➕ vert pour ajouter des personnes
- Interface de recherche dynamique
- Tapez au moins 2 caractères pour rechercher par :
  - Matricule
  - Nom
  - Prénom
- Sélectionnez les personnes en cliquant sur les résultats
- Supprimez une personne avec le bouton "✕"

#### Étape 3 : Section 🟠 "QUAND ?" - Temporalité

**Date d'observation** (obligatoire)
- Date et heure par défaut : maintenant
- Modifiable selon la date réelle d'observation
- Format : JJ/MM/AAAA HH:MM

**Date de déclaration**
- Affichée automatiquement (non modifiable)
- Horodatage de création de la déclaration

#### Étape 4 : Section 🟢 "OÙ ?" - Localisation

**Service concerné** (obligatoire)
- Liste hiérarchique triée alphabétiquement
- Votre service est automatiquement pré-sélectionné
- Navigation facilitée : services parents puis sous-services
- Format d'affichage : "Service Parent > Sous-Service"

**Lieu** (optionnel)
- Localisation précise où l'écart a été observé
- Champ de texte libre

#### Étape 5 : Section 🟣 "COMMENT ?" - Source et contexte
**Source de l'audit** (obligatoire)
- Sélectionnez la source de l'audit dans la liste déroulante
- Les options sont configurées par les administrateurs

**Processus SMI associé** (conditionnel)
- Ce champ apparaît automatiquement si la source d'audit l'exige
- Sélectionnez le processus concerné dans la liste

**Référence source** (optionnel)
- Référence externe de l'audit si applicable

#### Étape 6 : Ajouter des écarts individuels

**Écarts multiples**
- Utilisez le bouton ➕ "Ajouter un écart" pour créer plusieurs écarts dans la même déclaration
- Chaque écart nécessite :
  - **Type d'écart** : Sélection selon la source d'audit choisie
  - **Description** : Explication détaillée de l'écart observé

**Pièces jointes** (optionnel)
- Ajoutez des fichiers pour chaque écart ou pour la déclaration globale
- Formats supportés : PDF, images, documents
- Bouton 📎 "Ajouter une pièce jointe"

#### Étape 7 : Validation
- Cliquez sur **"Créer la déclaration"**
- Un message de succès confirme la création
- Redirection automatique vers la liste des écarts

### Consulter les déclarations et écarts

#### Deux vues disponibles
- **📋 Déclarations d'écart** : Vue des déclarations complètes avec filtres
- **📋 Liste des écarts** : Vue des écarts individuels

#### Interface de la liste des déclarations
La liste des déclarations offre une vue d'ensemble avec filtres intelligents :

**Filtrage avancé**
- **Filtre par service** : Services triés hiérarchiquement
- **Filtre par déclarant** : Recherche par nom, prénom ou matricule
- **Filtre par source d'audit** : Filtrer selon la source
- **Filtres par défaut** : Vos propres déclarations sont affichées automatiquement

**Colonnes affichées**
- **Écart** : Numéro d'écart (format EC-YYYY-XXXX) et description tronquée
- **Type** : Type d'écart configuré
- **Service** : Service concerné par l'écart
- **Source** : Source de l'audit ayant identifié l'écart
- **Statut** : État actuel (Déclaré, Rejeté, Fermé) avec code couleur
- **Déclaré le** : Date de création de l'écart

**Actions disponibles**
- 👁️ **Voir les détails** : Accès au détail complet de l'écart
- ✏️ **Modifier** : Édition de l'écart (selon les droits)

#### États et couleurs des écarts
- 🟡 **Déclaré** : Écart nouvellement créé (badge jaune)
- 🔴 **Rejeté** : Écart refusé après analyse (badge rouge)
- 🟢 **Fermé** : Écart traité et résolu (badge vert)

### Navigation et raccourcis

**Boutons rapides**
- **"Déclarer un écart"** disponible en permanence dans l'en-tête de liste
- **Message d'état vide** : Si aucun écart n'existe, bouton central pour démarrer

**Interface responsive**
- Les modales s'adaptent à la taille de l'écran
- Formulaires optimisés pour mobile et desktop
- Recherche d'utilisateurs fluide sur tous les appareils

### Bonnes pratiques

#### Pour les déclarants
1. **Soyez précis** : Décrivez clairement l'écart observé
2. **Documentez le contexte** : Renseignez le lieu et les personnes présentes
3. **Choisissez le bon service** : Vérifiez que le service sélectionné est correct
4. **Respectez les délais** : Déclarez rapidement après observation

#### Pour les gestionnaires
1. **Filtrez efficacement** : Utilisez les filtres pour traiter les écarts par service
2. **Suivez les statuts** : Surveillez l'évolution des écarts via les codes couleur
3. **Analysez les tendances** : Identifiez les services avec le plus d'écarts

### Droits et permissions

**Tous les utilisateurs authentifiés peuvent :**
- Déclarer des écarts
- Consulter la liste des écarts
- Voir les détails des écarts

**Les administrateurs peuvent en plus :**
- Modifier les écarts existants
- Configurer les sources d'audit, processus et types d'écarts
- Accéder aux fonctionnalités d'administration

### Résolution des problèmes courants

**"Le bouton ne fait rien"**
- Vérifiez votre connexion internet
- Rafraîchissez la page
- Vérifiez que JavaScript est activé

**"Je ne trouve pas un utilisateur"**
- Vérifiez l'orthographe du nom/matricule
- L'utilisateur doit être créé dans le système au préalable
- Contactez votre administrateur si nécessaire

**"Le champ processus n'apparaît pas"**
- C'est normal si la source d'audit ne l'exige pas
- Le champ apparaît automatiquement selon la source sélectionnée

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

**Accès requis** : Super Administrateur uniquement

L'interface Django Admin offre des fonctionnalités techniques avancées pour les super administrateurs.

#### Se connecter
1. Cliquez sur **Administration** → **Administration Django**
2. Vous êtes automatiquement connecté avec votre session active
3. Accédez au panneau d'administration technique

#### Fonctionnalités disponibles

##### Section "2. Services"
- **Liste des services** : Vue tableau avec filtres et recherche
- **Ajout/Modification** : Formulaires détaillés
- **Actions en masse** : Opérations sur plusieurs services
- **Import/Export** : Boutons d'import/export JSON

##### Section "3. Utilisateurs (Custom)"
- **Liste des utilisateurs** : Vue tableau avec tous les champs
- **Ajout/Modification** : Formulaires complets avec validation
- **Actions en masse** : Opérations sur plusieurs utilisateurs
- **Export JSON** : Sauvegarde des utilisateurs
- **Filtres avancés** : Par droits, service, dates

##### Fonctionnalités avancées
- **Filtres** : Par service parent, date de création, droits utilisateur
- **Recherche** : Par nom, code de service, matricule utilisateur
- **Tri** : Par colonnes (nom, code, date, matricule)
- **Pagination** : Navigation dans les listes longues
- **Actions en masse** : Modification multiple d'enregistrements

### Gestion technique avancée

#### Section "Authentification et autorisation" (Django standard)
- **Utilisateurs Django** : Comptes techniques (différent des utilisateurs métier)
- **Groupes** : Organisation par rôles Django
- **Permissions** : Droits granulaires sur les modèles

⚠️ **Important** : Ne pas confondre avec la gestion des utilisateurs métier accessible via le menu Administration principal.

## 🔧 Résolution des problèmes

### Problèmes fréquents

#### Problèmes d'authentification

##### Impossible de se connecter
**Symptôme** : "Matricule ou mot de passe incorrect" 
**Causes possibles** :
- Matricule mal saisi (format [A-Z][0-9]{4} requis)
- Mot de passe incorrect
- Compte désactivé ou supprimé
**Solutions** :
1. Vérifiez le format du matricule (ex: A1234)
2. Demandez une réinitialisation de mot de passe à un administrateur
3. Contactez votre administrateur système

##### Redirection forcée vers changement de mot de passe
**Symptôme** : Impossible d'accéder aux autres pages
**Cause** : Première connexion ou réinitialisation
**Solution** :
1. Changez votre mot de passe sur la page dédiée
2. Utilisez un mot de passe sécurisé (min. 8 caractères)

#### Problèmes de droits d'accès

##### Menu Administration invisible
**Symptôme** : Le menu Administration n'apparaît pas
**Cause** : Droits utilisateur insuffisants (niveau "US")
**Solution** :
1. Seuls les Administrateurs et Super Administrateurs voient ce menu
2. Demandez une élévation de droits à votre administrateur

##### Administration Django inaccessible
**Symptôme** : Lien "Administration Django" absent ou erreur d'accès
**Cause** : Seuls les Super Administrateurs ont accès
**Solution** :
1. Vérifiez votre niveau de droits
2. Demandez l'accès Super Administrateur si nécessaire

#### Problèmes de gestion des services

##### Impossible de supprimer un service
**Symptôme** : Message d'erreur lors de la suppression
**Cause** : Le service contient des sous-services
**Solution** :
1. Déplacez ou supprimez d'abord tous les sous-services
2. Recommencez la suppression du service parent

##### Erreur "Code déjà existant"
**Symptôme** : Impossible de créer/modifier un service ou utilisateur
**Cause** : Le code/matricule saisi existe déjà
**Solution** :
1. Vérifiez l'unicité du code ou matricule
2. Choisissez un identifiant différent
3. Ou modifiez l'enregistrement existant

#### Problèmes de gestion des utilisateurs

##### Erreur de format de matricule
**Symptôme** : "Le matricule doit contenir une lettre majuscule suivie de 4 chiffres"
**Cause** : Format de matricule incorrect
**Solution** :
1. Respectez le format exact : [A-Z][0-9]{4}
2. Exemples valides : A1234, B5678, Z9999
3. Exemples invalides : a1234, AB123, A12345

##### Impossible de supprimer un utilisateur
**Symptôme** : Bouton de suppression grisé ou absent
**Cause** : Tentative de suppression de son propre compte
**Solution** :
1. Un utilisateur ne peut pas supprimer son propre compte
2. Demandez à un autre administrateur de procéder à la suppression

##### Utilisateur ne peut pas se connecter après création
**Symptôme** : Nouvel utilisateur ne peut pas se connecter
**Causes possibles** :
- Mot de passe par défaut non communiqué
- Matricule mal saisi lors de la création
**Solutions** :
1. Vérifiez que le mot de passe par défaut est `azerty`
2. Vérifiez le matricule exact dans la liste des utilisateurs
3. Réinitialisez le mot de passe si nécessaire

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

**Utilisateur**
: Compte d'accès à l'application avec matricule, droits et informations personnelles.

**Matricule**
: Identifiant unique de l'utilisateur au format [Lettre][4 chiffres] (ex: A1234).

**Droits d'accès**
: Niveau d'autorisation déterminant les fonctionnalités accessibles (SA, AD, US).

**Super Administrateur (SA)**
: Niveau de droits maximum avec accès à toutes les fonctionnalités y compris Admin Django.

**Administrateur (AD)**
: Niveau de droits permettant la gestion des services et utilisateurs (sans Admin Django).

**Utilisateur (US)**
: Niveau de droits standard pour l'utilisation quotidienne sans accès administration.

**Import/Export JSON**
: Fonctionnalité de sauvegarde et restauration des données au format JSON.

**Authentification matricule**
: Système de connexion utilisant le matricule comme identifiant au lieu d'un nom d'utilisateur.

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

**🔄 Dernière mise à jour** : Août 2025

### Historique des versions

**Version 2.0** (Août 2025)
- ✨ **Nouvelle fonctionnalité** : Gestion complète des utilisateurs
- 🔐 **Authentification personnalisée** : Système de connexion par matricule
- 👥 **Système de droits** : 3 niveaux d'accès (Super Admin, Admin, User)
- 🎨 **Interface dédiée** : Templates de connexion et changement de mot de passe
- 🔒 **Sécurité renforcée** : Changement de mot de passe obligatoire à la première connexion
- 📋 **Export utilisateurs** : Fonctionnalité d'export JSON des utilisateurs
- 🛡️ **Modales de confirmation** : Système uniforme de confirmation pour toutes les suppressions
- ⚠️ **Avertissements intelligents** : Messages contextuels pour les suppressions avec dépendances

**Version 1.0** (Janvier 2025)
- 🏢 **Gestion des services** : CRUD complet avec hiérarchie
- 📥📤 **Import/Export JSON** : Sauvegarde et restauration des services
- 🎨 **Interface moderne** : Tailwind CSS + HTMX + Alpine.js
- ⚙️ **Administration Django** : Interface d'administration avancée