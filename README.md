# EcartsActions - Guide Développeur

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture technique](#architecture-technique)
- [Base de données et modèles](#base-de-données-et-modèles)
- [Installation et configuration](#installation-et-configuration)
- [Structure du projet](#structure-du-projet)
- [Stack technologique](#stack-technologique)
- [Conventions de développement](#conventions-de-développement)
- [Workflows de développement](#workflows-de-développement)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Maintenance](#maintenance)

## 🎯 Vue d'ensemble

EcartsActions est une application web moderne de **gestion d'écarts et d'actions** construite avec Django et une stack frontend moderne. L'application permet de gérer une structure organisationnelle hiérarchique avec des services/départements et leurs relations, ainsi que le suivi d'écarts et de plans d'actions.

### Fonctionnalités principales
- **Gestion des Services**: Organisation hiérarchique des départements/services avec tri alphabétique automatique
- **Gestion des Utilisateurs**: Système d'authentification personnalisé avec 3 niveaux de droits
- **Workflow de Validation Optimisé**: Interface compacte avec mise à jour dynamique en temps réel
- **Authentification Matricule**: Connexion par matricule (format: Lettre + 4 chiffres)
- **Interface moderne**: Navigation intuitive avec dropdowns hiérarchiques et transitions fluides
- **Import/Export JSON**: Sauvegarde et restauration des données (services et utilisateurs)
- **Modales de confirmation**: Système uniforme de confirmation pour toutes les opérations critiques
- **Performance Optimisée**: Templates cachés, requêtes optimisées, et réduction du FOUC

### 🚀 **Système d'Événements et d'Écarts**
- **Gestion des Événements**: Système complet de déclaration et suivi des événements avec classification écart/non-écart
- **Classification Conditionnelle**: Types d'événements avec champ booléen pour distinguer les vrais écarts des simples événements
- **Modal de Déclaration**: Interface structurée QUI/QUAND/OÙ/COMMENT pour saisir les événements
- **Pièces Jointes**: Support des attachements pour déclarations et écarts individuels
- **Statuts Différenciés**: Statuts complets pour les écarts, statuts limités (déclaré/annulé) pour les événements non-écarts
- **Badges Visuels**: Distinction visuelle avec badges "ÉCART" rouges pour identifier les vrais écarts
- **Historique des Modifications**: Suivi complet des changements avec signaux Django et logging détaillé

### 🔍 **Filtrage et Tri Avancés**
- **Vue Personnalisée par Défaut**: Affichage automatique des écarts/événements de son service + déclarés + impliqués
- **Filtrage Multi-Critères**: Service, déclarant (avec autocomplétion), type d'événement, source d'audit, statut
- **Filtrage par Type**: Cases à cocher pour afficher écarts et/ou événements (par défaut: écarts uniquement)
- **Tri Cliquable**: Tri par colonnes avec indicateurs visuels (flèches) sur toutes les listes
- **Interface Centrée**: Champs de filtres et boutons centrés pour une meilleure UX
- **Pré-remplissage Intelligent**: Champs service/déclarant auto-remplis en vue personnalisée

### 🔐 **Permissions et Sécurité**
- **Contrôle d'Accès Granulaire**: Seuls le déclarant, SA et AD peuvent modifier un écart/événement
- **Visibilité Conditionnelle**: Boutons de modification masqués selon les permissions
- **Filtrage Sécurisé**: Protection contre les injections avec validation des paramètres
- **Gestion des Sessions**: Middleware pour suivi des modifications par utilisateur

### ⚖️ **Système de Workflow de Validation**
- **Matrice Service × Source d'Audit × Niveau**: Affectation de valideurs avec dimension source d'audit intégrée
- **Interface Dropdown Minimaliste**: Navigation service → sources d'audit pour assignation simplifiée
- **Compteurs Dynamiques**: Affichage du nombre de sources non assignées par service
- **Tous Utilisateurs Éligibles**: Suppression des restrictions aux seuls administrateurs
- **Boutons d'Assignation Fonctionnels**: Correction du scope Alpine.js avec fonction globale
- **Design Épuré**: Suppression du bandeau d'avertissement global au profit d'indicateurs par service

### Objectifs techniques
- Interface utilisateur moderne et responsive
- Interactions fluides sans rechargement de page (HTMX)
- Composants réactifs côté client (Alpine.js)
- Modales pour les formulaires de création/modification
- Modales de confirmation centrées avec design uniforme
- Actions alignées visuellement avec icônes intuitives

### Philosophie technique
- **Progressive Enhancement**: L'application fonctionne sans JavaScript et s'améliore avec
- **HTMX-first**: Privilégier HTMX pour les interactions AJAX
- **Tailwind CSS**: Classes utilitaires pour un styling cohérent
- **Alpine.js**: Réactivité légère côté client quand nécessaire

## 🏗️ Architecture technique

### Architecture générale
```
Frontend (Browser)
├── Tailwind CSS (Styling)
├── HTMX (AJAX Interactions)
└── Alpine.js (Client Reactivity)
        ↕
Backend (Django)
├── Views (Business Logic)
├── Models (Data Layer)
├── Templates (HTML Generation)
└── Static Files (Assets)
        ↕
Database (SQLite)
├── Service (Hierarchical Organization)
└── User (Custom Authentication Model)
```

## 🗃️ Base de données et modèles

### Structure de la base de données

L'application utilise **SQLite** en développement avec une structure simple mais puissante pour gérer l'organisation hiérarchique et l'authentification personnalisée.

### Modèle User (Authentification personnalisée)

Le modèle `User` utilise l'authentification par matricule avec 3 niveaux de droits.

```python
class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    # Matricule unique (Lettre + 4 chiffres)
    matricule = models.CharField(max_length=5, unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    
    # Niveaux de droits
    SUPER_ADMIN = 'SA'  # Accès complet + Admin Django
    ADMIN = 'AD'        # Accès administratif (sans Admin Django)
    USER = 'US'         # Utilisateur standard
    
    droits = models.CharField(max_length=2, choices=DROITS_CHOICES, default=USER)
    service = models.ForeignKey(Service, null=True, blank=True)
    must_change_password = models.BooleanField(default=True)
```

#### Système d'authentification
- **Matricule**: Format requis `[A-Z][0-9]{4}` (ex: A1234)
- **Mot de passe par défaut**: `azerty` (changement obligatoire à la première connexion)
- **Interface dédiée**: Templates de connexion et changement de mot de passe personnalisés
- **Middleware**: Force le changement de mot de passe si nécessaire

#### Niveaux de droits et accès
| Niveau | Code | Accès Navigation | Accès Administration | Admin Django |
|--------|------|------------------|---------------------|--------------|
| Super Administrateur | `SA` | ✅ Tous menus | ✅ Services + Utilisateurs | ✅ Oui |
| Administrateur | `AD` | ✅ Tous menus | ✅ Services + Utilisateurs | ❌ Non |
| Utilisateur | `US` | ✅ Dashboard, Écarts, Actions | ❌ Aucun | ❌ Non |

### Modèle Service

Le modèle `Service` est le cœur de l'application, permettant de créer une structure organisationnelle complète.

```python
class Service(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, 
                              related_name='sous_services')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### Champs du modèle Service

| Champ | Type | Description | Contraintes |
|-------|------|-------------|-------------|
| `nom` | CharField(100) | Nom du service/département | Obligatoire |
| `code` | CharField(20) | Code unique d'identification | Unique, obligatoire |
| `parent` | ForeignKey(self) | Service parent dans la hiérarchie | Optionnel |
| `created_at` | DateTimeField | Date de création automatique | Auto-généré |
| `updated_at` | DateTimeField | Date de modification automatique | Auto-généré |

#### Relations hiérarchiques

```
Direction Générale (DG)
├── Direction des Ressources Humaines (DRH)
│   ├── Service Recrutement (REC)
│   └── Service Formation (FORM)
├── Direction Financière (DF)
│   ├── Comptabilité (COMPTA)
│   └── Contrôle de Gestion (CG)
└── Direction Technique (DT)
    ├── Bureau d'Études (BE)
    └── Service Maintenance (MAINT)
```

#### Méthodes du modèle Service

| Méthode | Description | Retour |
|---------|-------------|--------|
| `get_niveau()` | Calcule le niveau hiérarchique | `int` (0 = racine) |
| `get_chemin_hierarchique()` | Chemin complet depuis la racine | `str` ("DG > DRH > REC") |
| `get_descendants()` | Tous les sous-services récursivement | `QuerySet` |
| `get_descendants_count()` | Nombre total de descendants (tous niveaux) | `int` |
| `is_racine()` | Vérifie si c'est un service racine | `bool` |
| `clean()` | Validation des dépendances circulaires | `None` |

### Validations et contraintes

#### Validation des dépendances circulaires
```python
def clean(self):
    if self.parent and self.parent == self:
        raise ValidationError("Un service ne peut pas être son propre parent.")
    
    if self.parent and self._check_circular_dependency(self.parent):
        raise ValidationError("Cette relation créerait une dépendance circulaire.")
```

#### Exemples de dépendances interdites
- ❌ `Service A` → parent : `Service A` (auto-référence)
- ❌ `Service A` → `Service B` → `Service A` (cycle)
- ✅ `Service A` → `Service B` → `Service C` (hiérarchie valide)

### ⚖️ Modèle ValidateurService - Workflow Optimisé

Le modèle `ValidateurService` gère l'affectation de valideurs aux services avec une architecture optimisée pour les performances et l'UX.

```python
class ValidateurService(TimestampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='validateurs')
    audit_source = models.ForeignKey(AuditSource, on_delete=models.CASCADE)
    validateur = models.ForeignKey(User, on_delete=models.CASCADE)  # Tous les utilisateurs
    niveau = models.IntegerField(choices=[(1, 'Niveau 1'), (2, 'Niveau 2'), (3, 'Niveau 3')])
    actif = models.BooleanField(default=True)
```

#### ✨ Nouvelles Fonctionnalités (v2.3)

| Fonctionnalité | Description | Impact |
|----------------|-------------|--------|
| **Matrice Service × Source × Niveau** | Un valideur par combinaison | Granularité maximale |
| **Tous utilisateurs éligibles** | Plus de restriction aux seuls admins | Flexibilité d'assignation |
| **Interface compacte** | Badges réduits (w-6→w-5, w-4) | Affichage optimisé |
| **Mise à jour dynamique** | Badges d'aperçu temps réel | Aucun rechargement nécessaire |
| **Modal refait** | JavaScript vanilla stable | Tous les boutons fonctionnels |

#### Méthodes utilitaires

```python
# Récupérer les validateurs d'un service
ValidateurService.get_validateurs_service(service, niveau=1, actif_seulement=True)

# Services qu'un valideur peut valider  
ValidateurService.get_services_validateur(validateur, actif_seulement=True)

# Niveau maximum configuré pour un service
ValidateurService.get_niveaux_max_service(service)
```

#### Interface de gestion workflow

- **Page dédiée** : `/workflow/` accessible aux administrateurs
- **Matrice visuelle** : Tableau des services feuilles avec valideurs par niveau
- **Tri intelligent** : Par nom ou code de service avec indicateurs visuels
- **Assignation AJAX** : Modal pour ajouter/retirer des valideurs instantanément
- **Codes couleur** : Vert=Niveau 1, Bleu=Niveau 2, Violet=Niveau 3

### Interactions avec la base de données

#### Opérations CRUD

**Création d'un service**
```python
# Création d'un service racine
service_dg = Service.objects.create(
    nom="Direction Générale",
    code="DG"
)

# Création d'un sous-service
service_drh = Service.objects.create(
    nom="Direction des Ressources Humaines",
    code="DRH",
    parent=service_dg  # Référence au service parent
)
```

**Requêtes hiérarchiques**
```python
# Récupérer tous les services racines
services_racines = Service.objects.filter(parent=None)

# Récupérer tous les sous-services d'un service
sous_services = service_dg.sous_services.all()

# Recherche par niveau hiérarchique
services_niveau_2 = Service.objects.filter(
    parent__parent__isnull=False,
    parent__isnull=False
)
```

#### Import/Export JSON

**Format d'export**
```json
{
  "model": "Service",
  "export_date": "2024-01-28T10:30:00",
  "total_records": 5,
  "data": [
    {
      "id": 1,
      "nom": "Direction Générale",
      "code": "DG",
      "parent_id": null,
      "parent_code": null,
      "created_at": "2024-01-28T08:00:00",
      "updated_at": "2024-01-28T08:00:00"
    },
    {
      "id": 2,
      "nom": "Direction des Ressources Humaines",
      "code": "DRH",
      "parent_id": 1,
      "parent_code": "DG",
      "created_at": "2024-01-28T08:15:00",
      "updated_at": "2024-01-28T08:15:00"
    }
  ]
}
```

**Processus d'import**
1. **Validation du fichier** : Format JSON, structure attendue
2. **Tri hiérarchique** : Parents traités avant les enfants
3. **Résolution des conflits** : Mise à jour ou création selon le code
4. **Transaction atomique** : Rollback en cas d'erreur
5. **Rapport d'import** : Statistiques de création/mise à jour

#### Import/Export des Utilisateurs

**Format d'export utilisateurs**
```json
{
  "model": "User",
  "export_date": "2025-08-01T14:30:00.123456",
  "total_records": 3,
  "data": [
    {
      "id": 1,
      "matricule": "A1234",
      "nom": "Dupont",
      "prenom": "Jean",
      "email": "jean.dupont@entreprise.nc",
      "droits": "AD",
      "service_code": "DRH",
      "must_change_password": true,
      "is_staff": true,
      "is_superuser": false,
      "created_at": "2025-08-01T08:00:00.000000+00:00",
      "updated_at": "2025-08-01T08:00:00.000000+00:00",
      "last_login": "2025-08-01T10:30:00.000000+00:00"
    }
  ]
}
```

**Processus d'import utilisateurs**
1. **Suppression sécurisée** : Tous les utilisateurs supprimés sauf l'utilisateur actuel
2. **Réinitialisation des mots de passe** : Tous les utilisateurs importés reçoivent le mot de passe "azerty"
3. **Changement obligatoire** : `must_change_password=True` forcé pour tous les utilisateurs importés
4. **Association des services** : Lien automatique par code de service
5. **Protection administrateur** : L'utilisateur effectuant l'import est préservé
6. **Transaction atomique** : Import complet ou échec total (pas de demi-mesure)

### 🚀 Optimisations de performance

#### Requêtes optimisées pour le workflow
```python
# Workflow - Éviter N+1 queries avec préchargement optimisé
services_feuilles = Service.objects.filter(
    sous_services__isnull=True
).prefetch_related(
    Prefetch(
        'validateurs',
        queryset=ValidateurService.objects.filter(actif=True).select_related(
            'validateur', 'audit_source'
        )
    )
).order_by(order_field)

# Pré-construction d'un dictionnaire pour éliminer les requêtes N+1
validateurs_dict = {}
for service in services_feuilles:
    validateurs_dict[service.id] = {}
    for audit_source in audit_sources:
        validateurs_dict[service.id][audit_source.id] = {1: None, 2: None, 3: None}
```

#### Performance frontend - Réduction FOUC
```html
<!-- Préchargement des ressources critiques -->
<link rel="preconnect" href="https://cdn.tailwindcss.com">
<link rel="dns-prefetch" href="https://unpkg.com">

<!-- CSS critique en inline -->
<style>
    .pre-tailwind { visibility: hidden; }
    .tailwind-loaded .pre-tailwind { visibility: visible; }
</style>
```

#### Cache de développement
```python
# Templates cachés pour éviter rechargements constants
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [...])
]

# Cache en mémoire pour meilleures performances
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,
    }
}
```

### Migration et évolution du schéma

#### Migrations Django appliquées
```bash
# Migration initiale (création du modèle Service)
0001_initial.py

# Suppression du modèle Item (ancien modèle)
0002_delete_item.py

# Ajout des contraintes de validation
0003_add_service_constraints.py
```

#### Commandes utiles
```bash
# Vérifier les migrations en attente
python manage.py showmigrations

# Créer une nouvelle migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Rollback vers une migration précédente
python manage.py migrate core 0001
```

### Patterns d'architecture utilisés
- **MVT (Model-View-Template)**: Pattern Django standard
- **HTMX Patterns**: 
  - Swap HTML partials
  - Trigger events for updates
  - Progressive enhancement
- **Component-based Templates**: Templates modulaires et réutilisables

## ⚙️ Installation et configuration

### Prérequis
- Python 3.12.3+
- Git
- Virtual environment (venv)

### Installation locale

1. **Cloner le repository**
```bash
git clone <repository-url>
cd ecarts_actions
```

2. **Configurer l'environnement virtuel**
```bash
# L'environnement virtuel existe déjà
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

3. **Configuration de la base de données**
```bash
python manage.py migrate
python manage.py createsuperuser  # Optionnel
```

4. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

5. **Accéder à l'application**
- Application: http://127.0.0.1:8000/
- Admin Django: http://127.0.0.1:8000/admin/

### Variables d'environnement

Créer un fichier `.env` (optionnel pour le développement):
```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

## 📁 Structure du projet

### Architecture modulaire par domaine métier

```
ecarts_actions/
├── 📁 ecarts_actions/          # Configuration Django
│   ├── settings.py            # ⚙️ Configuration principale
│   ├── urls.py               # 🔗 URLs racine
│   ├── wsgi.py               # 🚀 Configuration WSGI
│   └── asgi.py               # 🚀 Configuration ASGI
├── 📁 core/                   # 🎯 Application principale
│   ├── 📁 models/             # 🗃️ Modèles par domaine
│   │   ├── __init__.py       # 📦 Import centralisé
│   │   ├── base.py           # 🏗️ Modèles abstraits (TimestampedModel, CodedModel)
│   │   ├── services.py       # 🏢 Modèle Service (organisation hiérarchique)
│   │   ├── users.py          # 👤 Modèle User (authentification personnalisée)
│   │   ├── gaps.py           # ⚠️ Modèles GapReport, Gap, GapType, AuditSource pour gestion complète des écarts
│   │   ├── attachments.py    # 📎 Modèles GapReportAttachment, GapAttachment pour pièces jointes
│   │   ├── workflow.py       # ⚖️ Modèle ValidateurService pour gestion workflow de validation
│   │   └── actions.py        # 📋 Modèles Action, PlanAction (à venir)
│   ├── 📁 views/              # 👁️ Vues par domaine
│   │   ├── __init__.py       # 📦 Import centralisé
│   │   ├── dashboard.py      # 📊 Vue tableau de bord
│   │   ├── services.py       # 🏢 CRUD services + import/export
│   │   ├── users.py          # 👤 CRUD utilisateurs + gestion droits + import/export
│   │   ├── auth.py           # 🔐 Authentification personnalisée
│   │   ├── gaps.py           # ⚠️ Gestion complète des écarts qualité avec filtrage intelligent et permissions
│   │   ├── workflow.py       # ⚖️ Gestion workflow : affectation valideurs par service et niveau
│   │   └── actions.py        # 📋 Gestion des plans d'actions (à venir)
│   ├── 📁 admin/              # 🔧 Configuration admin par domaine
│   │   ├── __init__.py       # 📦 Import centralisé
│   │   ├── services.py       # 🏢 ServiceAdmin
│   │   ├── users.py          # 👤 UserAdmin
│   │   ├── gaps.py           # ⚠️ Administration des écarts qualité
│   │   └── actions.py        # 📋 ActionAdmin (à venir)
│   ├── urls.py               # 🔗 URLs de l'app
│   └── migrations/           # 📦 Migrations DB
├── 📁 templates/              # 🎨 Templates par domaine
│   ├── base.html             # 🏠 Template de base avec Tailwind/HTMX/Alpine
│   ├── 📁 admin/              # 🔧 Templates admin personnalisés
│   │   ├── core/service/     # 🏢 Templates import/export services
│   │   └── core/user/        # 👤 Templates import/export utilisateurs
│   └── 📁 core/               # 📁 Templates de l'app core
│       ├── 📁 dashboard/      # 📊 Templates tableau de bord
│       │   └── dashboard.html # 📊 Page principale dashboard
│       ├── 📁 auth/           # 🔐 Templates authentification
│       │   ├── login.html    # 🔑 Page de connexion personnalisée
│       │   └── change_password.html # 🔒 Changement mot de passe
│       ├── 📁 services/       # 🏢 Templates gestion services
│       │   ├── list.html     # 📋 Liste hiérarchique des services
│       │   ├── item.html     # 📄 Item service (récursif)
│       │   ├── detail.html   # 🔍 Détail d'un service
│       │   ├── form.html     # 📝 Formulaire service
│       │   ├── form_modal.html # 📝 Formulaire modal HTMX
│       │   ├── notification_confirm.html # ⚠️ Modale confirmation suppression
│       │   ├── notification_warning.html # ⚠️ Modale warning suppression
│       │   └── notification_error.html   # ❌ Modale erreur suppression
│       ├── 📁 users/          # 👤 Templates gestion utilisateurs
│       │   ├── list.html     # 📋 Liste des utilisateurs
│       │   ├── item.html     # 📄 Item utilisateur
│       │   ├── detail.html   # 🔍 Détail d'un utilisateur
│       │   ├── form.html     # 📝 Formulaire utilisateur
│       │   ├── form_modal.html # 📝 Formulaire modal HTMX
│       │   ├── notification_confirm.html # ⚠️ Modale confirmation suppression
│       │   ├── notification_warning.html # ⚠️ Modale warning suppression
│       │   ├── notification_error.html   # ❌ Modale erreur suppression
│       │   └── icons.html    # 🎨 Icônes utilisateurs
│       ├── 📁 gaps/           # ⚠️ Templates gestion des écarts qualité
│       │   ├── gap_list.html  # 📋 Liste des écarts individuels
│       │   ├── gap_report_list.html # 📋 Liste des déclarations avec filtrage intelligent
│       │   ├── gap_report_detail.html # 🔍 Détail déclaration avec écarts restructurés
│       │   ├── gap_report_form.html # 📝 Formulaire modification déclaration
│       │   ├── gap_report_form_modal.html # 📝 Modal déclaration structuré QUI/QUAND/OÙ/COMMENT
│       │   ├── gap_form.html  # 📝 Formulaire écart avec styling cohérent et badges colorés
│       │   └── partials/      # 🧩 Composants HTMX (champs dynamiques, processus)
│       ├── 📁 workflow/       # ⚖️ Templates gestion workflow
│       │   └── management.html # 📊 Matrice valideurs par service avec tri et assignation AJAX
│       └── 📁 actions/        # 📋 Templates gestion actions (à venir)
├── 📁 static/                 # 🎭 Fichiers statiques
│   ├── css/                  # 🎨 CSS personnalisés
│   ├── js/                   # ⚡ JavaScript personnalisés
│   │   ├── gaps.js          # ⚠️ Logique interactive pour les écarts
│   │   └── common.js        # 🔧 Fonctions utilitaires communes
│   └── images/               # 🖼️ Images
├── 📁 media/                  # 📎 Fichiers téléchargés (pièces jointes)
├── 📁 venv/                   # 🐍 Environnement virtuel Python 3.12.3
├── manage.py                 # 🛠️ CLI Django
├── requirements.txt          # 📦 Dépendances Python
├── README.md                 # 📖 Documentation développeur
├── MANUEL.md                 # 📋 Manuel utilisateur
└── CLAUDE.md                 # 🤖 Guide Claude Code
```

### Principe de l'architecture modulaire

#### 🏗️ Organisation par domaine métier
Chaque domaine métier (services, écarts, actions) est organisé dans sa propre structure :
- **Modèles** : `models/domaine.py` - Logique de données
- **Vues** : `views/domaine.py` - Logique métier et interaction
- **Admin** : `admin/domaine.py` - Configuration interface d'administration
- **Templates** : `templates/core/domaine/` - Interface utilisateur

#### 📦 Import centralisé
Les fichiers `__init__.py` permettent d'importer tous les composants d'un domaine :
```python
# core/models/__init__.py
from .services import Service
from .ecarts import Ecart, TypeEcart  # À venir
from .actions import Action, PlanAction  # À venir

# core/views/__init__.py
from .dashboard import dashboard
from .services import services_list, service_create, service_edit
```

#### 🔄 Évolutivité et maintenance
- **Ajout facile** de nouveaux domaines métier
- **Séparation claire** des responsabilités
- **Tests isolés** par domaine
- **Réutilisabilité** des composants de base
- **Collaboration** facilitée (plusieurs développeurs)

## 🛠️ Stack technologique

### Backend
- **Django 5.2.4**: Framework web Python
- **SQLite**: Base de données (développement)
- **Django Compressor**: Compression des assets statiques

### Frontend
- **Tailwind CSS**: Framework CSS utility-first
- **HTMX 1.9.10**: Interactions AJAX sans JavaScript complexe
- **Alpine.js 3.x**: Réactivité côté client légère

### Outils de développement
- **Python 3.12.3**: Langage de programmation
- **Git**: Contrôle de version
- **VS Code**: IDE recommandé

## 📏 Conventions de développement

### Architecture modulaire par domaine

#### 🗂️ Organisation des fichiers
Suivre la structure modulaire pour tous les nouveaux domaines métier :

```python
# ✅ Correct : Organisation par domaine
core/
├── models/
│   ├── __init__.py          # Import centralisé
│   ├── base.py              # Modèles abstraits réutilisables
│   ├── services.py          # Domaine services
│   ├── ecarts.py            # Domaine écarts
│   └── actions.py           # Domaine actions
├── views/
│   ├── __init__.py          # Import centralisé
│   ├── dashboard.py         # Vue transversale
│   ├── services.py          # Vues domaine services
│   ├── ecarts.py            # Vues domaine écarts
│   └── actions.py           # Vues domaine actions
```

#### 📦 Règles d'import centralisé
Chaque module doit exposer ses composants via `__init__.py` :

```python
# core/models/__init__.py
from .services import Service
from .ecarts import Ecart, TypeEcart, StatutEcart
from .actions import Action, PlanAction, Responsable

# Permet d'importer simplement :
from core.models import Service, Ecart, Action
```

#### 🏗️ Modèles de base
Utiliser les modèles abstraits pour la cohérence :

```python
# Utiliser les modèles de base
from .base import TimestampedModel, CodedModel

class NouveauModele(TimestampedModel, CodedModel):
    nom = models.CharField(max_length=100)
    # Hérite automatiquement de : created_at, updated_at, code
```

### Conventions Python/Django
- **PEP 8**: Style guide Python standard
- **Django Conventions**: Nommage des modèles, vues, URLs
- **Docstrings**: Documentation des fonctions et classes avec format Google/NumPy
- **Type Hints**: Utiliser les annotations de type quand c'est pertinent

### Conventions Frontend
- **Tailwind Classes**: Utiliser les classes Tailwind plutôt que du CSS custom
- **HTMX Attributes**: Préfixer avec `hx-` et documenter les interactions
- **Alpine.js**: Utiliser `x-data`, `x-show`, etc. avec parcimonie

### Conventions de nommage par domaine
```python
# Modèles : PascalCase avec préfixe domaine si nécessaire
class Service(models.Model):          # ✅ Simple et clair
class EcartQualite(models.Model):     # ✅ Préfixe si ambigu
class Action(models.Model):           # ✅ Simple et clair

# Vues : snake_case avec préfixe domaine
def services_list(request):           # ✅ services_list
def service_create(request):          # ✅ service_create
def ecart_validate(request):          # ✅ ecart_validate

# URLs : kebab-case avec préfixe domaine
path('services/', views.services_list, name='services-list')
path('services/create/', views.service_create, name='service-create')
path('ecarts/validate/<int:pk>/', views.ecart_validate, name='ecart-validate')

# Templates : Organisation par dossier domaine
templates/core/services/list.html     # ✅ Organisé par domaine
templates/core/services/form.html     # ✅ Nom explicite
templates/core/ecarts/detail.html     # ✅ Cohérent
```

### Structure des fichiers par domaine

#### 📝 Template d'un nouveau domaine
```python
# core/models/nouveau_domaine.py
"""
Modèles liés au domaine [Nom du domaine].
Description du domaine et de ses responsabilités.
"""
from django.db import models
from .base import TimestampedModel, CodedModel

class NouveauModele(TimestampedModel, CodedModel):
    """Documentation du modèle."""
    nom = models.CharField(max_length=100, verbose_name="Nom")
    
    class Meta:
        verbose_name = "N. Nouveau Modèle"  # N = ordre d'affichage
        verbose_name_plural = "N. Nouveaux Modèles"
        
    def __str__(self):
        return f"{self.code} - {self.nom}"
```

```python
# core/views/nouveau_domaine.py
"""
Vues pour la gestion du domaine [Nom du domaine].
"""
from django.shortcuts import render, get_object_or_404
from ..models import NouveauModele

def nouveau_domaine_list(request):
    """Vue liste du domaine."""
    items = NouveauModele.objects.all()
    return render(request, 'core/nouveau_domaine/list.html', {
        'items': items
    })
```

#### 🗂️ Organisation des templates
```
templates/core/nouveau_domaine/
├── list.html           # Liste des éléments
├── detail.html         # Détail d'un élément
├── form.html           # Formulaire standard
├── form_modal.html     # Formulaire modal HTMX
└── item.html           # Item dans une liste (si récursif)
```

### Structure des commits
```
type(scope): description

feat(core): add item creation functionality
fix(ui): correct modal closing behavior
docs(readme): update installation instructions
style(css): improve button styling
refactor(views): simplify item_create logic
test(core): add item model tests
```

## 🔄 Workflows de développement

### Workflow Git
1. **Créer une branche feature**
   ```bash
   git checkout -b feature/nom-de-la-feature
   ```

2. **Développer la fonctionnalité**
   - Faire des commits atomiques
   - Mettre à jour README.md et MANUEL.md si nécessaire

3. **Avant chaque commit**
   ```bash
   # Vérifier les migrations
   python manage.py makemigrations --dry-run
   
   # Vérifier que les tests passent
   python manage.py test
   
   # Mettre à jour la documentation
   # - README.md (si changements techniques)
   # - MANUEL.md (si changements fonctionnels)
   ```

4. **Push et Pull Request**
   ```bash
   git push origin feature/nom-de-la-feature
   # Créer une PR sur GitHub/GitLab
   ```

### Développement avec HTMX

#### Pattern de base HTMX
```html
<!-- Bouton qui déclenche une requête HTMX -->
<button 
    hx-get="/items/create/"
    hx-target="#modal-container"
    class="btn-primary">
    Créer un élément
</button>

<!-- Container qui recevra la réponse -->
<div id="modal-container"></div>
```

#### Pattern de formulaire modal
```python
# Vue qui retourne soit le formulaire soit la réponse
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            # Retourner HTML partial pour mise à jour
            html = render_to_string('core/item_row.html', {'item': item})
            response = HttpResponse(html)
            response['HX-Trigger'] = 'itemCreated'  # Déclencher un événement
            return response
    else:
        form = ItemForm()
    return render(request, 'core/item_form_modal.html', {'form': form})
```

### Développement avec Alpine.js

#### Pattern de base Alpine.js
```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open">Contenu conditionnel</div>
</div>
```

## 🧪 Tests

### Lancer les tests
```bash
# Tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test core

# Tests avec couverture
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère un rapport HTML
```

### Structure des tests
```python
# core/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from .models import Item

class ItemModelTest(TestCase):
    def test_item_creation(self):
        item = Item.objects.create(title="Test Item")
        self.assertEqual(item.title, "Test Item")

class ItemViewTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_item_list_view(self):
        response = self.client.get(reverse('item-list'))
        self.assertEqual(response.status_code, 200)
```

## 🚀 Déploiement

### Préparation pour la production
1. **Variables d'environnement**
   ```bash
   DEBUG=False
   SECRET_KEY=production-secret-key
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   ALLOWED_HOSTS=yourdomain.com
   ```

2. **Collecte des fichiers statiques**
   ```bash
   python manage.py collectstatic
   ```

3. **Migrations**
   ```bash
   python manage.py migrate
   ```

### Configuration serveur web
- **Nginx**: Configuration pour servir les fichiers statiques
- **Gunicorn**: Serveur WSGI pour Django
- **PostgreSQL**: Base de données de production

## 🔧 Maintenance

### Mise à jour des dépendances
```bash
# Vérifier les dépendances obsolètes
pip list --outdated

# Mettre à jour une dépendance
pip install --upgrade django

# Mettre à jour requirements.txt
pip freeze > requirements.txt
```

### Sauvegarde de la base de données
```bash
# Export
python manage.py dumpdata > backup.json

# Import
python manage.py loaddata backup.json
```

### Monitoring et logs
- **Django Debug Toolbar**: Outil de debug en développement
- **Logging**: Configuration dans settings.py
- **Sentry**: Monitoring des erreurs en production (optionnel)

## 📚 Ressources et documentation

### Documentation officielle
- [Django Documentation](https://docs.djangoproject.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Guides et tutoriels
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [HTMX + Django Guide](https://htmx.org/essays/django-and-htmx/)
- [Tailwind + Django Setup](https://django-tailwind.readthedocs.io/)

---

## 🆕 Changements récents

### v2.4.0 - Interface Workflow Dropdown Minimaliste avec Gestion Sources d'Audit (2025-08-08)

#### 📊 Nouvelle architecture Service × Source d'Audit × Niveau
- **Dimension source d'audit intégrée** : Modèle ValidateurService étendu avec AuditSource comme foreign key
- **Contrainte unique restructurée** : `['service', 'audit_source', 'niveau']` pour éviter les conflits
- **Migration avec valeur par défaut** : `default=1` (Audit interne/AFNOR) pour les enregistrements existants
- **Méthode get_validateurs_service améliorée** : Ajout du paramètre `audit_source`

#### 🎨 Interface Dropdown Minimaliste
- **Suppression bandeau d'avertissement global** : Plus de grande zone rouge perturbante
- **Compteurs par service** : Format "X/Y non assignées" (rouge) ou "✓ Y/Y configurées" (vert)
- **Navigation dropdown intuitive** : Clic service → dépliage sources d'audit en ligne
- **Layout réorganisé** : Source d'audit à gauche, niveaux à droite pour clarté visuelle

#### ⚙️ Corrections Techniques Critiques
- **Boutons d'assignation fonctionnels** : Résolution du problème de scope Alpine.js
- **Fonction globale window.openAssignModal** : Contournement élégant des limitations x-data
- **Échappement JavaScript correct** : Usage de `escapejs` pour gérer les apostrophes
- **Pont Alpine.js** : Accès au data stack pour déclenchement modal depuis DOM global

#### 🎯 Améliorations UX
- **Suppression des restrictions admin** : Tous les utilisateurs peuvent être valideurs
- **Interface plus compacte** : Hauteur de lignes augmentée mais design épuré
- **Flèche rotative** : Animation 90° pour indiquer l'état du dropdown
- **Badges couleur par niveau** : Vert/Bleu/Violet avec bouton suppression intégré

#### 🛠️ Refactoring Backend
- **Vues workflow restructurées** : assign_validator() et remove_validator() gèrent audit_source_id
- **API service_detail_api()** : Endpoint JSON pour chargement dynamique des sources par service
- **search_users() étendu** : Recherche sur tous les utilisateurs au lieu des seuls admins
- **Validation étendue** : clean() vérifie l'unicité service/audit_source/niveau

### v2.3.0 - Système de Workflow de Validation (2025-08-07)

#### ⚖️ Nouveau modèle de workflow
- **Modèle ValidateurService** : Gestion complète des affectations valideurs par service et niveau
- **3 niveaux de validation** : Système flexible avec 1, 2 ou 3 niveaux selon les besoins
- **Contraintes métier** : Seuls les administrateurs (SA/AD) peuvent être valideurs
- **Services feuilles uniquement** : Configuration limitée aux services terminaux sans sous-services

#### 🎯 Interface de gestion intuitive
- **Matrice visuelle** : Tableau avec services en lignes et niveaux en colonnes
- **Codes couleur distincts** : Vert=Niveau 1, Bleu=Niveau 2, Violet=Niveau 3
- **Légende explicite** : Explication des niveaux en haut de page
- **Compteur de services** : Nombre de services feuilles affichés

#### 🔧 Fonctionnalités d'assignation
- **Modal HTMX** : Interface d'assignation moderne avec Alpine.js
- **Assignation AJAX** : Ajout de valideurs sans rechargement de page
- **Suppression intuitive** : Bouton "×" sur chaque badge de valideur
- **Gestion des doublons** : Prévention automatique des affectations multiples

#### 📊 Tri et organisation
- **Tri alphabétique par défaut** : Services triés par nom A→Z automatiquement
- **Tri cliquable** : En-tête "Service" cliquable pour inverser l'ordre
- **Tri par code** : Clic sur le code d'un service pour trier par code
- **Indicateurs visuels** : Flèches indiquant l'ordre de tri actuel

#### 🛠️ Améliorations techniques  
- **Migration dédiée** : `0013_validateurservice.py` pour le nouveau modèle
- **API endpoints** : URLs complètes pour assignation/suppression via AJAX
- **Template tags personnalisés** : Système simplifié sans dépendances externes
- **Gestion d'erreurs robuste** : Messages explicites et fallbacks appropriés

#### 🎨 Navigation intégrée
- **Menu Administration** : Lien "Gestion du workflow" ajouté au menu existant
- **Restriction d'accès** : Accessible uniquement aux SA/AD
- **Icône dédiée** : Icône de validation pour identification rapide
- **Design cohérent** : Suit les conventions visuelles de l'application

### v2.2.0 - Système de suppression d'écarts avec popup et gestion déclarations (2025-08-04)

#### 🗑️ Suppression d'écarts avec confirmation élégante
- **Popup de confirmation**: Même style que les services/agents avec HTMX + Alpine.js
- **Messages contextuels**: Avertissement spécial si c'est le dernier écart d'une déclaration
- **Permissions strictes**: Seuls SA/AD peuvent supprimer des écarts
- **Suppression complète**: Écart + pièces jointes supprimés proprement

#### 🔗 Suppression automatique des déclarations vides
- **Détection du dernier écart**: Système intelligent qui détecte quand c'est le dernier écart
- **Suppression en cascade**: Déclaration + pièces jointes automatiquement supprimées
- **Message d'avertissement clair**: "⚠️ ATTENTION" avec détail de ce qui sera supprimé
- **Redirection intelligente**: Vers la liste des déclarations si déclaration supprimée

#### 🔢 Correction de la numérotation des écarts
- **Gestion des "trous"**: Réutilise les numéros disponibles après suppression
- **Algorithme optimisé**: Trouve le premier numéro libre dans la séquence
- **Résolution des conflits**: Correction de l'erreur UNIQUE constraint failed
- **Numérotation cohérente**: Maintient l'ordre logique des écarts

#### 🎨 Interface de suppression unifiée
- **Bouton croix**: Cohérent avec le design existant des services/agents
- **Modal Alpine.js**: Animations fluides et fermeture intuitive
- **JavaScript robuste**: Fallback automatique si HTMX non disponible
- **Gestion d'erreurs**: Messages explicites et redirection appropriée

#### 🛠️ Améliorations techniques
- **HTMX programmatique**: Utilisation de `htmx.ajax()` pour plus de contrôle
- **Transactions atomiques**: Suppression sécurisée avec rollback en cas d'erreur
- **Cleanup des fichiers**: Suppression physique des pièces jointes du disque
- **URLs cohérentes**: API endpoints suivant les conventions du projet

### v2.1.0 - Améliorations majeures du système d'écarts (2025-08-04)

#### 🎯 Filtrage intelligent des déclarations
- **Vue personnalisée par défaut**: Affiche automatiquement les écarts du service de l'utilisateur + déclarés par lui + où il est impliqué
- **Bouton "Tout voir"**: Permet de voir toutes les déclarations de l'organisation
- **Bannières contextuelles**: Indication visuelle du mode de filtrage actif

#### 🔐 Permissions administratives renforcées
- **Super Administrateurs (SA)** et **Administrateurs (AD)** peuvent modifier toutes les déclarations
- **Badge "Admin"** visible sur les boutons de modification pour indiquer les droits étendus
- **Messages d'erreur explicites** pour les utilisateurs sans droits suffisants

#### 🎨 Interface écarts repensée
- **Affichage restructuré**: Numéro d'écart + type sur la première ligne, description en dessous
- **Boutons icônes uniquement**: Cohérence avec la page des services
- **Statut et actions alignés**: Meilleure lisibilité visuelle

#### 📝 Formulaires cohérents
- **Styling uniforme**: Formulaires d'écart alignés sur le style des déclarations
- **Badges colorés**: Sections "QUOI ?" (violet) et "POURQUOI ?" (orange)
- **Champs pleine largeur**: Description adaptée à la largeur de l'encart
- **Nettoyage des redondances**: Suppression des informations dupliquées

#### 🛠️ Améliorations techniques
- **Logique de filtrage optimisée**: Détection précise des paramètres de recherche
- **Gestion des erreurs de template**: Résolution des problèmes de syntaxe Django
- **Classes CSS centralisées**: Définition dans les widgets de formulaire Django

---

**📝 Note importante**: Ce README.md doit être mis à jour avant chaque commit qui introduit des changements techniques, architecturaux ou de configuration.