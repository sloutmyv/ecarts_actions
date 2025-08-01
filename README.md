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
- **Gestion des Services**: Organisation hiérarchique des départments/services
- **Gestion des Utilisateurs**: Système d'authentification personnalisé avec 3 niveaux de droits
- **Authentification Matricule**: Connexion par matricule (format: Lettre + 4 chiffres)
- **Interface moderne**: Navigation intuitive avec dropdowns hiérarchiques
- **Import/Export JSON**: Sauvegarde et restauration des données organisationnelles
- **Modales de confirmation**: Système uniforme de confirmation pour les suppressions
- **Gestion des Écarts**: Suivi et traitement des non-conformités (à venir)
- **Plans d'Actions**: Planification et suivi des actions correctives (à venir)

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

### Optimisations de performance

#### Requêtes optimisées
```python
# Éviter N+1 queries avec select_related
services = Service.objects.select_related('parent')

# Précharger les sous-services
services = Service.objects.prefetch_related('sous_services')

# Requête complète optimisée
services = Service.objects.select_related('parent').prefetch_related('sous_services')
```

#### Index de base de données
- Index automatique sur `id` (clé primaire)
- Index automatique sur `code` (contrainte unique)
- Index automatique sur `parent_id` (clé étrangère)

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
│   │   ├── ecarts.py         # ⚠️ Modèles Écart, TypeEcart (à venir)
│   │   └── actions.py        # 📋 Modèles Action, PlanAction (à venir)
│   ├── 📁 views/              # 👁️ Vues par domaine
│   │   ├── __init__.py       # 📦 Import centralisé
│   │   ├── dashboard.py      # 📊 Vue tableau de bord
│   │   ├── services.py       # 🏢 CRUD services + import/export
│   │   ├── users.py          # 👤 CRUD utilisateurs + gestion droits
│   │   ├── auth.py           # 🔐 Authentification personnalisée
│   │   ├── ecarts.py         # ⚠️ Gestion des écarts (à venir)
│   │   └── actions.py        # 📋 Gestion des plans d'actions (à venir)
│   ├── 📁 admin/              # 🔧 Configuration admin par domaine
│   │   ├── __init__.py       # 📦 Import centralisé
│   │   ├── services.py       # 🏢 ServiceAdmin
│   │   ├── users.py          # 👤 UserAdmin
│   │   ├── ecarts.py         # ⚠️ EcartAdmin (à venir)
│   │   └── actions.py        # 📋 ActionAdmin (à venir)
│   ├── urls.py               # 🔗 URLs de l'app
│   └── migrations/           # 📦 Migrations DB
├── 📁 templates/              # 🎨 Templates par domaine
│   ├── base.html             # 🏠 Template de base avec Tailwind/HTMX/Alpine
│   ├── 📁 admin/              # 🔧 Templates admin personnalisés
│   │   └── core/service/     # 🏢 Templates import/export services
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
│       ├── 📁 ecarts/         # ⚠️ Templates gestion écarts (à venir)
│       └── 📁 actions/        # 📋 Templates gestion actions (à venir)
├── 📁 static/                 # 🎭 Fichiers statiques
│   ├── css/                  # 🎨 CSS personnalisés
│   ├── js/                   # ⚡ JavaScript personnalisés
│   └── images/               # 🖼️ Images
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

**📝 Note importante**: Ce README.md doit être mis à jour avant chaque commit qui introduit des changements techniques, architecturaux ou de configuration.