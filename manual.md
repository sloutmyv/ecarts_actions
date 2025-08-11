# Manuel Utilisateur - EcartsActions

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Premiers pas](#premiers-pas)
- [Gestion des écarts](#gestion-des-écarts)
- [Workflow de validation](#workflow-de-validation)
- [Administration](#administration)
- [FAQ](#faq)

## 🎯 Vue d'ensemble

EcartsActions est une application de **gestion d'écarts et d'événements** qui permet de déclarer, suivre et traiter les écarts qualité au sein de votre organisation.

### Concepts clés

- **Événement** : Toute observation ou incident déclaré
- **Écart** : Événement qualifié comme non-conforme nécessitant un suivi
- **Déclaration** : Document regroupant un ou plusieurs écarts/événements
- **Validation** : Processus d'approbation des écarts par les validateurs désignés
- **Statut** : État actuel d'un écart (Déclaré, Retenu, Non retenu, Clos)

## 🚀 Premiers pas

### Connexion à l'application

1. **Accès** : Rendez-vous sur l'URL de l'application
2. **Matricule** : Saisissez votre matricule (format: 1 lettre + 4 chiffres, ex: A1234)
3. **Mot de passe** : Utilisez le mot de passe fourni par votre administrateur

> ℹ️ **Premier accès** : Vous devrez changer votre mot de passe lors de la première connexion

### Interface principale

L'interface se compose de :
- **Menu de navigation** : Accès aux différentes sections
- **Tableau de bord** : Vue d'ensemble de vos écarts
- **Filtres** : Outils de recherche et de tri
- **Actions** : Boutons pour créer, modifier, valider

## 📊 Gestion des écarts

### Déclarer un nouvel événement

1. **Accès** : Cliquez sur "Nouvelle déclaration" dans le menu Écarts
2. **Informations générales** :
   - **Source d'audit** : Choisissez d'où provient l'observation
   - **Référence source** : Numéro de référence (optionnel)
   - **Service concerné** : Service où l'événement s'est produit
   - **Lieu** : Localisation précise
   - **Date d'observation** : Quand l'événement s'est produit

3. **Personnes impliquées** :
   - Recherchez et sélectionnez les personnes présentes lors de l'observation
   - Utilisez l'autocomplétion pour trouver rapidement les utilisateurs

4. **Description des écarts** :
   - **Type d'écart** : Sélectionnez le type selon la source d'audit
   - **Description** : Décrivez précisément ce qui s'est passé
   - Ajoutez autant d'écarts que nécessaire

5. **Pièces jointes** :
   - Ajoutez des documents, photos ou preuves
   - Formats supportés : PDF, Word, Excel, images, etc.

### Consulter et filtrer les écarts

#### Vue par défaut
Par défaut, vous voyez :
- Les écarts de votre service et ses sous-services
- Les écarts que vous avez déclarés
- Les écarts où vous êtes impliqué

#### Filtres disponibles
- **Service** : Filtrage hiérarchique (inclut les sous-services)
- **Statut** : Déclaré, Retenu, Non retenu, Clos, Annulé
- **Type d'événement** : Écarts uniquement, événements uniquement, ou les deux
- **Source d'audit** : ISO, réglementaire, interne, etc.
- **Déclarant/Impliqué** : Recherche par nom ou matricule

#### Tri des colonnes
Cliquez sur les en-têtes de colonnes pour trier :
- Numéro d'écart
- Type d'écart
- Service
- Source d'audit
- Statut
- Date de création
- Déclarant

### Modifier un écart

**Qui peut modifier ?**
- Le déclarant de l'écart
- Les administrateurs (SA et AD)

**Restrictions** :
- Seuls les écarts "Déclarés" ou "Annulés" peuvent être modifiés
- Les écarts en cours de validation ou clos ne peuvent plus être modifiés

### Supprimer un écart

**Qui peut supprimer ?**
- Seuls les Super Administrateurs (SA) et Administrateurs (AD)

**Conditions** :
- L'écart doit être "Déclaré" ou "Annulé"
- Si c'est le dernier écart d'une déclaration, toute la déclaration sera supprimée

## ⚖️ Workflow de validation

### Comprendre la validation

Le système de validation fonctionne par **niveaux hiérarchiques** :
- **Niveau 1** : Premier validateur
- **Niveau 2** : Validation intermédiaire
- **Niveau 3** : Validation finale

### Processus de validation

1. **Notification** : Les validateurs reçoivent une notification quand un écart nécessite leur validation
2. **Examen** : Le validateur examine l'écart et ses détails
3. **Décision** : Approuver ou rejeter avec un commentaire obligatoire en cas de rejet
4. **Propagation** : Si approuvé, l'écart passe au niveau suivant

### Modification directe de statut

**Qui peut modifier directement ?**
- Les administrateurs (SA et AD)
- **Les validateurs du niveau le plus élevé uniquement**

> ⚠️ **Important** : Seuls les validateurs ayant le niveau de validation le plus élevé configuré pour un service/source d'audit peuvent modifier directement le statut des écarts.

**Statuts disponibles** :
- **Retenu** : L'écart est confirmé et nécessite un suivi
- **Non retenu** : L'écart n'est pas confirmé
- **Clos** : L'écart est traité et fermé

**Traçabilité** :
- Tous les changements de statut apparaissent dans l'historique des validations
- Les modifications directes sont clairement identifiées

### Historique des validations

L'historique montre :
- **Validations classiques** : "a approuvé" ou "a rejeté"
- **Modifications directes** : "a modifié le statut directement"
- **Niveau de validation** : Niveau du validateur
- **Commentaires** : Justifications et détails
- **Horodatage** : Date et heure précises

## 🔧 Administration

### Gestion des utilisateurs

**Niveaux de droits** :
- **Super Administrateur (SA)** : Accès complet, y compris l'admin Django
- **Administrateur (AD)** : Accès administratif sans l'admin Django
- **Utilisateur (US)** : Accès standard aux écarts et actions

**Fonctionnalités** :
- Création, modification, activation/désactivation des comptes
- Import/Export des utilisateurs en JSON
- Affectation aux services
- Gestion des mots de passe

### Gestion des services

**Organisation hiérarchique** :
- Structure en arbre avec services parents et sous-services
- Codes uniques pour chaque service
- Activation/désactivation sans perte de données

**Import/Export** :
- Sauvegarde complète de la structure
- Restauration depuis fichier JSON

### Configuration des validateurs

**Matrice de validation** :
- Assignation par Service × Source d'audit × Niveau
- Chaque combinaison peut avoir jusqu'à 3 niveaux de validation
- Interface simplifiée avec compteurs par service

**Règles** :
- Un seul validateur par niveau par combinaison service/source
- Tous les utilisateurs peuvent être validateurs
- Activation/désactivation sans perte d'historique

## ❓ FAQ

### Questions générales

**Q : Comment récupérer mon mot de passe ?**
R : Contactez votre administrateur système. Il peut réinitialiser votre mot de passe.

**Q : Pourquoi ne vois-je pas tous les écarts ?**
R : Par défaut, vous ne voyez que les écarts de votre périmètre (votre service + déclarés + impliqué). Utilisez "Afficher tout" pour voir l'ensemble.

**Q : Quelle est la différence entre écart et événement ?**
R : Un événement est toute observation déclarée. Un écart est un événement qualifié comme non-conforme nécessitant un suivi spécifique.

### Validation et statuts

**Q : Pourquoi ne puis-je pas modifier le statut d'un écart ?**
R : Seuls les validateurs du niveau le plus élevé pour votre service/source d'audit peuvent modifier directement les statuts. Vérifiez votre niveau d'habilitation.

**Q : Que signifie "a modifié le statut directement" dans l'historique ?**
R : Cela indique qu'un validateur a changé directement le statut de l'écart sans passer par le workflow de validation classique.

**Q : Puis-je annuler une validation ?**
R : Non, une fois validé, un écart ne peut être modifié que par les administrateurs ou via un changement de statut direct.

### Problèmes techniques

**Q : Le site est lent, que faire ?**
R : L'application est optimisée pour 400+ utilisateurs. Si vous rencontrez des lenteurs, contactez l'support technique.

**Q : Mes pièces jointes ne s'uploadent pas**
R : Vérifiez la taille (max 20 MB) et le format de vos fichiers. Formats supportés : PDF, Word, Excel, images, etc.

**Q : Je ne reçois pas les notifications**
R : Les notifications apparaissent dans l'interface. Vérifiez votre rôle de validateur pour les services concernés.

---

## 📞 Support

Pour toute question ou problème :
- Contactez votre administrateur système
- Consultez cette documentation
- Vérifiez vos permissions et niveau d'accès

---

*Dernière mise à jour : 11 août 2025 - Version 2.7.0*