# EcartsActions - Manuel Utilisateur

## 📋 Table des matières

- [Introduction](#introduction)
- [Accès à l'application](#accès-à-lapplication)
- [Interface utilisateur](#interface-utilisateur)
- [Gestion des éléments](#gestion-des-éléments)
- [Fonctionnalités avancées](#fonctionnalités-avancées)
- [Administration](#administration)
- [Dépannage](#dépannage)
- [FAQ](#faq)

## 🎯 Introduction

### Qu'est-ce qu'EcartsActions ?

EcartsActions est une application web moderne de gestion d'éléments et de tâches conçue pour offrir une expérience utilisateur fluide et intuitive. L'application permet de créer, modifier, organiser et suivre des éléments de travail avec une interface responsive qui s'adapte à tous les appareils.

### Objectifs de l'application
- Centraliser la gestion des éléments/tâches
- Offrir une interface moderne et intuitive
- Permettre une collaboration efficace entre les utilisateurs
- Fournir un suivi en temps réel des activités

### Publics cibles
- **Administrateurs métier**: Gestion globale et configuration
- **Utilisateurs finaux**: Création et gestion des éléments
- **Superviseurs**: Suivi et reporting

## 🔐 Accès à l'application

### URL d'accès
- **Application principale**: https://votre-domaine.com/
- **Interface d'administration**: https://votre-domaine.com/admin/

### Authentification
1. **Accéder à la page de connexion**
2. **Saisir vos identifiants**:
   - Nom d'utilisateur
   - Mot de passe
3. **Cliquer sur "Se connecter"**

### Gestion des comptes
- **Création de compte**: Contactez votre administrateur système
- **Mot de passe oublié**: Utilisez le lien "Mot de passe oublié" sur la page de connexion
- **Modification du profil**: Accessible via le menu utilisateur

## 🖥️ Interface utilisateur

### Vue d'ensemble de l'interface

L'interface d'EcartsActions est conçue pour être intuitive et moderne :

#### Barre de navigation supérieure
- **Logo et nom de l'application** (côté gauche)
- **Menu principal** avec les fonctionnalités principales
- **Boutons d'action rapide** (Ajouter un élément)
- **Menu utilisateur** (côté droit) avec profil et déconnexion

#### Zone de contenu principal
- **Liste des éléments** avec vue tabulaire ou en cartes
- **Filtres et recherche** pour organiser l'affichage
- **Boutons d'action** sur chaque élément

#### Interface responsive
- **Version desktop**: Interface complète avec tous les éléments visibles
- **Version tablette**: Interface adaptée avec menus optimisés
- **Version mobile**: Interface simplifiée avec navigation par menus déroulants

### Navigation et interactions

#### Interactions sans rechargement
L'application utilise une technologie moderne qui permet :
- **Ajout d'éléments** via des modales (fenêtres contextuelles)
- **Modification en place** sans quitter la page
- **Suppression instantanée** avec confirmation
- **Mise à jour automatique** de l'affichage

#### Boutons d'action combinés (Split Buttons)
Certains éléments disposent de boutons d'action combinés :
- **Action principale** (côté gauche) : Action la plus courante
- **Menu déroulant** (côté droit) : Actions supplémentaires

## 📝 Gestion des éléments

### Création d'un nouvel élément

1. **Cliquer sur "Ajouter un élément"** dans la barre de navigation
2. **Remplir le formulaire** dans la modale qui s'ouvre :
   - **Titre** (obligatoire) : Nom de l'élément
   - **Description** (optionnel) : Détails de l'élément
   - **Catégorie** : Classification de l'élément
     - 🔵 Travail
     - 🟢 Personnel
     - 🔴 Urgent
     - ⚫ Autre
   - **Statut** : État actuel de l'élément
     - 🟡 À faire
     - 🔵 En cours
     - 🟢 Terminé
   - **Priorité** : Niveau d'importance (1=Basse, 2=Moyenne, 3=Haute)
3. **Cliquer sur "Créer"** pour valider
4. **L'élément apparaît automatiquement** dans la liste

### Consultation des éléments

#### Liste principale
- **Vue tabulaire** : Affichage en tableau avec colonnes
- **Informations visibles** :
  - Titre et description
  - Catégorie (avec code couleur)
  - Statut actuel
  - Priorité
  - Dates de création et modification

#### Détails d'un élément
- **Cliquer sur le titre** d'un élément pour voir ses détails
- **Modale de détail** avec toutes les informations
- **Historique des modifications** (si activé)

### Modification d'un élément

1. **Localiser l'élément** dans la liste
2. **Cliquer sur le bouton d'édition** (crayon) ou utiliser le split button
3. **Modifier les informations** dans la modale qui s'ouvre
4. **Cliquer sur "Modifier"** pour valider les changements
5. **L'affichage se met à jour automatiquement**

### Suppression d'un élément

1. **Localiser l'élément** à supprimer
2. **Cliquer sur le bouton de suppression** (poubelle) ou via le split button
3. **Confirmer la suppression** dans la boîte de dialogue
4. **L'élément disparaît automatiquement** de la liste

⚠️ **Attention** : La suppression est définitive et ne peut pas être annulée.

### Filtrage et recherche

#### Filtres disponibles
- **Par catégorie** : Afficher seulement certaines catégories
- **Par statut** : Filtrer selon l'état des éléments
- **Par priorité** : Afficher selon le niveau d'importance
- **Par date** : Éléments créés dans une période donnée

#### Recherche textuelle
- **Barre de recherche** en haut de la liste
- **Recherche dans** : Titre et description
- **Recherche en temps réel** : Résultats instantanés

## ⚡ Fonctionnalités avancées

### Actions en lot
- **Sélection multiple** : Cocher plusieurs éléments
- **Actions groupées** :
  - Changement de statut en masse
  - Modification de catégorie
  - Suppression multiple

### Export et import
- **Export** : Télécharger la liste au format CSV/Excel
- **Import** : Importer des éléments depuis un fichier

### Notifications
- **Notifications en temps réel** pour les actions importantes
- **Messages de confirmation** pour les actions réussies
- **Alertes d'erreur** en cas de problème

### Raccourcis clavier
- **Ctrl + N** : Nouvel élément
- **Échap** : Fermer les modales
- **Ctrl + F** : Recherche
- **Entrée** : Valider les formulaires

## 🔧 Administration

### Interface d'administration Django

L'application dispose d'une interface d'administration complète accessible aux administrateurs :

#### Accès à l'administration
1. **Se rendre sur** `/admin/`
2. **Se connecter** avec un compte administrateur
3. **Naviguer** dans les différentes sections

#### Gestion des utilisateurs
- **Création** de nouveaux comptes utilisateurs
- **Attribution** des permissions et groupes
- **Désactivation** de comptes si nécessaire
- **Réinitialisation** des mots de passe

#### Gestion des éléments
- **Vue administrative** de tous les éléments
- **Modification en masse** des données
- **Export** pour reporting
- **Suppression** avec confirmation

#### Configuration système
- **Paramètres généraux** de l'application
- **Configuration** des catégories et statuts
- **Gestion** des permissions et accès

### Maintenance et monitoring

#### Surveillance du système
- **Monitoring** des performances
- **Logs** d'activité et d'erreurs
- **Statistiques** d'utilisation

#### Sauvegarde des données
- **Sauvegarde automatique** quotidienne
- **Export manuel** des données
- **Procédure de restauration** en cas de problème

## 🆘 Dépannage

### Problèmes courants

#### L'application ne se charge pas
1. **Vérifier la connexion internet**
2. **Actualiser la page** (F5 ou Ctrl+R)
3. **Vider le cache** du navigateur
4. **Contacter l'administrateur** si le problème persiste

#### Les modales ne s'ouvrent pas
1. **Vérifier que JavaScript est activé**
2. **Désactiver les bloqueurs de publicité** temporairement
3. **Essayer avec un autre navigateur**
4. **Signaler le problème** à l'équipe technique

#### Problèmes de performance
1. **Fermer les onglets inutiles**
2. **Vider le cache** du navigateur
3. **Redémarrer le navigateur**
4. **Vérifier la connexion réseau**

#### Erreurs de sauvegarde
1. **Vérifier les champs obligatoires**
2. **Réessayer l'opération**
3. **Actualiser la page** et recommencer
4. **Contacter le support** si l'erreur persiste

### Messages d'erreur fréquents

| Message | Cause probable | Solution |
|---------|----------------|----------|
| "Champ obligatoire" | Information manquante | Remplir tous les champs marqués * |
| "Session expirée" | Connexion trop ancienne | Se reconnecter |
| "Erreur de réseau" | Problème de connexion | Vérifier la connexion internet |
| "Accès refusé" | Permissions insuffisantes | Contacter l'administrateur |

### Navigateurs supportés

#### Navigateurs recommandés
✅ **Chrome** (version 90+)  
✅ **Firefox** (version 88+)  
✅ **Safari** (version 14+)  
✅ **Edge** (version 90+)

#### Navigateurs non supportés
❌ **Internet Explorer** (toutes versions)  
❌ **Versions obsolètes** des navigateurs listés

## ❓ FAQ

### Questions générales

**Q : Puis-je utiliser l'application sur mon téléphone ?**  
R : Oui, l'application est entièrement responsive et s'adapte aux écrans mobiles et tablettes.

**Q : Mes données sont-elles sauvegardées automatiquement ?**  
R : Oui, toutes les modifications sont sauvegardées instantanément et des sauvegardes automatiques sont effectuées quotidiennement.

**Q : Puis-je récupérer un élément supprimé par erreur ?**  
R : Non, les suppressions sont définitives. Contactez l'administrateur qui pourra éventuellement récupérer les données depuis une sauvegarde.

**Q : Combien d'éléments puis-je créer ?**  
R : Il n'y a pas de limite définie pour les utilisateurs standard. Les limitations dépendent de la configuration du serveur.

### Questions techniques

**Q : Pourquoi l'application ne fonctionne-t-elle pas avec Internet Explorer ?**  
R : L'application utilise des technologies modernes non supportées par Internet Explorer. Utilisez un navigateur moderne.

**Q : Les modales ne se ferment pas, que faire ?**  
R : Cliquez en dehors de la modale ou appuyez sur la touche Échap. Si cela ne fonctionne pas, actualisez la page.

**Q : Comment signaler un bug ?**  
R : Contactez l'équipe de support en décrivant précisément le problème, les étapes pour le reproduire et votre environnement (navigateur, système d'exploitation).

### Questions de sécurité

**Q : Mon mot de passe est-il sécurisé ?**  
R : Oui, les mots de passe sont chiffrés et stockés de manière sécurisée. Choisissez un mot de passe fort et unique.

**Q : Puis-je partager mon compte avec un collègue ?**  
R : Non, chaque utilisateur doit avoir son propre compte pour des raisons de sécurité et de traçabilité.

**Q : Comment me déconnecter de manière sécurisée ?**  
R : Utilisez toujours le bouton "Déconnexion" dans le menu utilisateur, surtout sur un ordinateur partagé.

---

## 📞 Support et contact

### Équipe de support
- **Email support** : support@votredomaine.com
- **Téléphone** : +33 X XX XX XX XX
- **Horaires** : Lundi-Vendredi 9h-18h

### Ressources supplémentaires
- **Base de connaissances** : https://support.votredomaine.com
- **Formations** : Disponibles sur demande
- **Mises à jour** : Annoncées par email

---

**📝 Note importante** : Ce manuel utilisateur doit être mis à jour avant chaque commit qui introduit des changements fonctionnels visibles par les utilisateurs finaux.