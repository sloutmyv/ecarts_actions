# EcartsActions - Guide Développeur

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Installation et configuration](#installation-et-configuration)
- [Déploiement en production](#déploiement-en-production)
- [Architecture technique](#architecture-technique)
- [Base de données et modèles](#base-de-données-et-modèles)
- [Stack technologique](#stack-technologique)
- [Conventions de développement](#conventions-de-développement)
- [Structure du projet](#structure-du-projet)
- [Workflows de développement](#workflows-de-développement)
- [Tests](#tests)
- [Maintenance](#maintenance)
- [Changements récents](#changements-récents)

## 🎯 Vue d'ensemble

EcartsActions est une application web moderne de **gestion d'écarts et d'actions** construite avec Django et optimisée pour 400+ utilisateurs concurrents. L'application permet de gérer une structure organisationnelle hiérarchique avec des services/départements et leurs relations, ainsi que le suivi d'écarts et de plans d'actions.

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
- **Filtrage Hiérarchique des Services**: Les utilisateurs d'un service parent voient automatiquement les écarts de leurs services enfants
- **Filtrage Utilisateur Étendu**: Recherche par déclarant ou impliqué (personnes présentes lors de l'observation)
- **Filtrage Multi-Critères**: Service, déclarant/impliqué (avec autocomplétion), type d'événement, source d'audit, statut
- **Filtrage par Type**: Cases à cocher pour afficher écarts et/ou événements (par défaut: écarts uniquement)
- **Tri Cliquable**: Tri par colonnes avec indicateurs visuels (flèches) sur toutes les listes
- **Interface Centrée**: Champs de filtres et boutons centrés pour une meilleure UX
- **Pré-remplissage Intelligent**: Champs service/déclarant auto-remplis en vue personnalisée
- **Suppression avec Redirection Intelligente**: Retour contextuel selon la page d'origine (liste écarts vs détail déclaration)

### 🔐 **Permissions et Sécurité**
- **Contrôle d'Accès Granulaire**: Seuls le déclarant, SA et AD peuvent modifier un écart/événement
- **Visibilité Conditionnelle**: Boutons de modification masqués selon les permissions
- **Filtrage Sécurisé**: Protection contre les injections avec validation des paramètres
- **Gestion des Sessions**: Middleware pour suivi des modifications par utilisateur

### 🎛️ **Gestion de l'Activation/Désactivation et Sécurité**
- **Services Actifs/Inactifs**: Désactivation des services sans suppression pour préserver l'historique
- **Utilisateurs Actifs/Inactifs**: Blocage d'authentification des comptes inactifs avec conservation des données
- **Contraintes Hiérarchiques**: Impossible de désactiver un service parent avec des sous-services actifs
- **Protection Personnelle**: Impossible de désactiver son propre compte utilisateur
- **Interface Administrative**: Badges visuels (✓ ACTIF / ✗ INACTIF) et actions en lot dans l'admin Django
- **Filtrage Intelligent**: Services/utilisateurs inactifs masqués des listes de sélection mais historique préservé
- **Permissions Strictes**: Seuls Admin et Super Admin peuvent activer/désactiver services et utilisateurs
- **Autocomplétion Filtrée**: Recherche utilisateur ne retourne que les comptes actifs
- **Authentification Sécurisée**: Utilisateurs inactifs ne peuvent plus se connecter à l'application
- **Validation de Suppression Complète**: Impossible de supprimer services/utilisateurs avec dépendances actives (écarts, validateurs)
- **Protection des Validateurs**: Utilisateurs validateurs de workflow protégés contre suppression/désactivation
- **Messages d'Erreur Centrés**: Interface utilisateur avec notifications centrées sur la page
- **Compteurs Temps Réel**: Affichage du nombre d'éléments actifs sur les pages de gestion

### ⚖️ **Système de Workflow de Validation**
- **Matrice Service × Source d'Audit × Niveau**: Affectation de valideurs avec dimension source d'audit intégrée
- **Interface Dropdown Minimaliste**: Navigation service → sources d'audit pour assignation simplifiée
- **Compteurs Dynamiques**: Affichage du nombre de sources non assignées par service
- **Tous Utilisateurs Éligibles**: Suppression des restrictions aux seuls administrateurs
- **Boutons d'Assignation Fonctionnels**: Correction du scope Alpine.js avec fonction globale
- **Design Épuré**: Suppression du bandeau d'avertissement global au profit d'indicateurs par service

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

## 🚀 Déploiement en production

### Optimisations implémentées

#### 1. Base de données PostgreSQL
- **Migration** : SQLite → PostgreSQL avec pool de connexions
- **Configuration** : 20 connexions max, 5 min, durée de vie 5 min
- **Index** : 21 nouveaux index pour optimiser les requêtes fréquentes

#### 2. Cache Redis Distribué
- **Cache applicatif** : Redis DB 1 (5 minutes)
- **Sessions** : Redis DB 2 (24 heures) 
- **Templates** : Redis DB 3 (1 heure)
- **Pool** : 100 connexions pour cache, 50 pour sessions

#### 3. Pagination et Optimisation des Requêtes
- **Pagination** : 25 écarts par page, 20 déclarations par page
- **Select/Prefetch** : Optimisation des relations N+1
- **Cache intelligent** : Données référentielles en cache (services, types d'écarts)

#### 4. Transactions Concurrentielles Améliorées
- **Retry automatique** : 3 tentatives avec backoff exponentiel
- **NOWAIT locks** : Évite les blocages longs
- **Optimisation** : Génération de numéros d'écart optimisée

#### 5. Monitoring et Logging
- **Requêtes lentes** : Log automatique > 1 seconde
- **Usage DB** : Surveillance requêtes excessives (> 20)
- **Debug Toolbar** : Développement uniquement
- **Headers debug** : Pour administrateurs

### Prérequis de déploiement

#### Serveur
- **OS** : Ubuntu 20.04+ ou équivalent
- **RAM** : 4 GB minimum, 8 GB recommandé
- **CPU** : 2 cores minimum, 4 cores recommandé
- **Stockage** : SSD recommandé

#### Logiciels
```bash
# PostgreSQL 12+
sudo apt-get install postgresql postgresql-contrib

# Redis 6+
sudo apt-get install redis-server

# Python 3.12
sudo apt-get install python3.12 python3.12-venv

# Nginx (reverse proxy)
sudo apt-get install nginx
```

### Configuration de production

#### 1. Base de données PostgreSQL
```sql
-- Créer la base et l'utilisateur
CREATE DATABASE ecarts_actions;
CREATE USER ecarts_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ecarts_actions TO ecarts_user;
ALTER USER ecarts_user CREATEDB; -- Pour les tests
```

#### 2. Configuration PostgreSQL (`/etc/postgresql/12/main/postgresql.conf`)
```ini
# Optimisations pour 400 utilisateurs concurrents
max_connections = 200
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
```

#### 3. Redis (`/etc/redis/redis.conf`)
```ini
# Optimisations pour cache
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 4. Variables d'environnement
```bash
# Copier le fichier exemple
cp .env.example .env

# Variables de production dans .env
DB_NAME=ecarts_actions
DB_USER=ecarts_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1
USE_POSTGRESQL=1
USE_REDIS=1
SECRET_KEY=your-production-secret-key
DEBUG=0
ALLOWED_HOSTS=your-domain.com
```

#### 5. Installation et migrations
```bash
# Créer l'environnement virtuel
python3.12 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer l'utilisateur administrateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

#### 6. Gunicorn (serveur WSGI)
```bash
# Installer Gunicorn
pip install gunicorn

# Démarrer avec 8 workers (2 × CPU cores)
gunicorn ecarts_actions.wsgi:application \
    --workers 8 \
    --bind 127.0.0.1:8000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30
```

#### 7. Service Systemd
```ini
# /etc/systemd/system/ecarts_actions.service
[Unit]
Description=EcartsActions Django app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/ecarts_actions
Environment=PATH=/path/to/ecarts_actions/venv/bin
EnvironmentFile=/path/to/ecarts_actions/.env
ExecStart=/path/to/ecarts_actions/venv/bin/gunicorn ecarts_actions.wsgi:application --workers 8 --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 8. Nginx (reverse proxy)
```nginx
# /etc/nginx/sites-available/ecarts_actions
upstream ecarts_actions {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 20M;
    
    location /static/ {
        alias /path/to/ecarts_actions/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/ecarts_actions/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://ecarts_actions;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### Tests de performance

#### Test de charge avec Apache Bench
```bash
# Test avec 100 utilisateurs concurrents
ab -n 1000 -c 100 http://your-domain.com/gaps/

# Test de création d'écarts
ab -n 500 -c 50 -p post_data.txt -T "application/x-www-form-urlencoded" \
   http://your-domain.com/gaps/create/
```

#### Surveillance continue
```bash
# Surveiller les logs de performance
tail -f /var/log/ecarts_actions/performance.log

# Surveiller PostgreSQL
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Surveiller Redis
redis-cli info stats
```

### Validation du déploiement

#### Tests fonctionnels
1. ✅ Connexion utilisateur
2. ✅ Création d'écart
3. ✅ Pagination des listes
4. ✅ Filtrage et recherche
5. ✅ Upload de pièces jointes
6. ✅ Historique des modifications

#### Tests de performance
1. ✅ 400 utilisateurs simultanés supportés
2. ✅ Temps de réponse < 2s
3. ✅ Pas de deadlocks PostgreSQL
4. ✅ Cache Redis opérationnel
5. ✅ Logs de performance actifs

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
Database (SQLite/PostgreSQL)
├── Service (Hierarchical Organization)
└── User (Custom Authentication Model)
```

### Patterns d'architecture utilisés
- **MVT (Model-View-Template)**: Pattern Django standard
- **HTMX Patterns**: 
  - Swap HTML partials
  - Trigger events for updates
  - Progressive enhancement
- **Component-based Templates**: Templates modulaires et réutilisables

## 🗃️ Base de données et modèles

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

### Import/Export JSON

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
      "is_superuser": false
    }
  ]
}
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
│   │   ├── gaps.py           # ⚠️ Modèles GapReport, Gap, GapType, AuditSource
│   │   ├── attachments.py    # 📎 Modèles GapReportAttachment, GapAttachment
│   │   ├── workflow.py       # ⚖️ Modèle ValidateurService
│   │   └── actions.py        # 📋 Modèles Action, PlanAction (à venir)
│   ├── 📁 views/              # 👁️ Vues par domaine
│   │   ├── __init__.py       # 📦 Import centralisé
│   │   ├── dashboard.py      # 📊 Vue tableau de bord
│   │   ├── services.py       # 🏢 CRUD services + import/export
│   │   ├── users.py          # 👤 CRUD utilisateurs + gestion droits
│   │   ├── auth.py           # 🔐 Authentification personnalisée
│   │   ├── gaps.py           # ⚠️ Gestion complète des écarts qualité
│   │   ├── workflow.py       # ⚖️ Gestion workflow valideurs
│   │   └── actions.py        # 📋 Gestion plans d'actions (à venir)
│   ├── 📁 admin/              # 🔧 Configuration admin par domaine
│   ├── urls.py               # 🔗 URLs de l'app
│   ├── 📁 utils/              # 🔧 Utilitaires
│   │   ├── cache.py          # Cache intelligent
│   │   └── pagination.py     # Pagination optimisée
│   ├── middleware.py         # Middleware performance
│   └── migrations/           # 📦 Migrations DB
├── 📁 templates/              # 🎨 Templates par domaine
│   ├── base.html             # 🏠 Template de base avec Tailwind/HTMX/Alpine
│   └── 📁 core/               # Templates de l'app core
│       ├── 📁 dashboard/      # 📊 Templates tableau de bord
│       ├── 📁 auth/           # 🔐 Templates authentification
│       ├── 📁 services/       # 🏢 Templates gestion services
│       ├── 📁 users/          # 👤 Templates gestion utilisateurs
│       ├── 📁 gaps/           # ⚠️ Templates gestion écarts
│       ├── 📁 workflow/       # ⚖️ Templates gestion workflow
│       └── 📁 actions/        # 📋 Templates actions (à venir)
├── 📁 static/                 # 🎭 Fichiers statiques
│   ├── css/                  # 🎨 CSS personnalisés
│   ├── js/                   # ⚡ JavaScript personnalisés
│   └── images/               # 🖼️ Images
├── 📁 media/                  # 📎 Fichiers téléchargés
├── 📁 logs/                   # 📝 Logs application
├── 📁 venv/                   # 🐍 Environnement virtuel
├── manage.py                 # 🛠️ CLI Django
├── requirements.txt          # 📦 Dépendances Python
├── README.md                 # 📖 Documentation complète
├── MANUEL.md                 # 📋 Manuel utilisateur
├── CLAUDE.md                 # 🤖 Guide Claude Code
└── .env.example              # 🔧 Variables d'environnement
```

### Principe de l'architecture modulaire

#### 🏗️ Organisation par domaine métier
Chaque domaine métier (services, écarts, actions) est organisé dans sa propre structure :
- **Modèles** : `models/domaine.py` - Logique de données
- **Vues** : `views/domaine.py` - Logique métier et interaction
- **Admin** : `admin/domaine.py` - Configuration interface d'administration
- **Templates** : `templates/core/domaine/` - Interface utilisateur

## 🛠️ Stack technologique

### Backend
- **Django 5.2.4**: Framework web Python
- **SQLite**: Base de données (développement)
- **PostgreSQL**: Base de données (production)
- **Redis**: Cache distribué (production)
- **Django Compressor**: Compression des assets statiques

### Frontend
- **Tailwind CSS**: Framework CSS utility-first
- **HTMX 1.9.10**: Interactions AJAX sans JavaScript complexe
- **Alpine.js 3.x**: Réactivité côté client légère

### Outils de développement
- **Python 3.12.3**: Langage de programmation
- **Git**: Contrôle de version
- **VS Code**: IDE recommandé
- **Django Debug Toolbar**: Debug en développement

## 📏 Conventions de développement

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

### Conventions Python/Django
- **PEP 8**: Style guide Python standard
- **Django Conventions**: Nommage des modèles, vues, URLs
- **Docstrings**: Documentation des fonctions et classes
- **Type Hints**: Utiliser les annotations de type

### Conventions Frontend
- **Tailwind Classes**: Utiliser les classes Tailwind plutôt que du CSS custom
- **HTMX Attributes**: Préfixer avec `hx-` et documenter les interactions
- **Alpine.js**: Utiliser `x-data`, `x-show`, etc. avec parcimonie

## 🔄 Workflows de développement

### Workflow Git
1. **Créer une branche feature**
   ```bash
   git checkout -b feature/nom-de-la-feature
   ```

2. **Développer la fonctionnalité**
   - Faire des commits atomiques
   - Mettre à jour README.md si nécessaire

3. **Avant chaque commit**
   ```bash
   # Vérifier les migrations
   python manage.py makemigrations --dry-run
   
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
# Export SQLite
python manage.py dumpdata > backup.json

# Export PostgreSQL
pg_dump ecarts_actions > backup_$(date +%Y%m%d).sql

# Import
python manage.py loaddata backup.json
```

### Nettoyage périodique
```bash
# Vider le cache Redis si nécessaire
redis-cli FLUSHALL

# Nettoyer les sessions expirées
python manage.py clearsessions
```

## 📚 Ressources et documentation

### Documentation officielle
- [Django Documentation](https://docs.djangoproject.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

## 🆕 Changements récents

### v2.14.0 - Système de Notifications Dynamiques et Interface Améliorée (2025-08-15)

#### 🔄 Notifications dynamiques pour écarts/événements
- **Mise à jour automatique** : Les notifications de validation s'adaptent dynamiquement quand un écart devient un événement
- **Suppression intelligente** : Notifications de validation supprimées automatiquement quand `is_gap` passe de `True` à `False`
- **Création automatique** : Notifications de validation créées automatiquement quand `is_gap` passe de `False` à `True`
- **Double sécurité** : Détection via changement de `gap_type` ET nettoyage systématique pour garantir la cohérence
- **Notifications aux déclarants** : Information automatique des utilisateurs lors des reclassements écart ↔ événement

#### 🎯 Interface de liste améliorée
- **Boutons de modification grisés** : Option "Modifier" désactivée visuellement pour écarts retenus/rejetés (non-administrateurs)
- **Permissions granulaires** : Administrateurs (SA/AD) conservent tous les droits de modification
- **Indicateurs visuels** : Icône grisée avec tooltip explicatif "Modification non autorisée (écart retenu/non retenu)"
- **Cohérence UX** : Bouton actif pour écarts déclarés/annulés, grisé pour écarts finalisés

#### 🛠️ Signaux Django optimisés
- **Architecture centralisée** : Gestion unifiée des changements via signaux `Gap` et `GapType`
- **Extraction robuste des IDs** : Gestion correcte des données de changement en format `{'id': X, 'str': 'Y'}`
- **Nettoyage systématique** : Suppression automatique des notifications orphelines à chaque modification
- **Gestion d'erreur silencieuse** : Traitement robuste des erreurs sans impact sur l'expérience utilisateur

#### 🔧 Corrections techniques
- **Erreur CSRF résolue** : Configuration `CSRF_TRUSTED_ORIGINS` et `ALLOWED_HOSTS` pour localhost:8001
- **Dashboard corrigé** : Indicateur "Écarts" affiche maintenant `total_ecarts` au lieu de `evenements_non_ecarts`
- **Template sécurisé** : Condition de grisage utilisant comparaisons directes sans filtre `split` inexistant
- **Code épuré** : Suppression des logs de débogage et de la commande de nettoyage manuel devenue obsolète

#### 🚀 Workflow utilisateur simplifié
- **Plus de notifications parasites** : Les validateurs ne reçoivent que les notifications pertinentes
- **Adaptation temps réel** : Changements de type reflétés immédiatement dans les notifications
- **Cohérence garantie** : Double mécanisme (détection + nettoyage) pour éliminer les incohérences
- **Interface intuitive** : Boutons grisés indiquent clairement les limitations selon le statut et les droits

## 🆕 Changements récents

### v2.13.0 - Historique des Pièces Jointes et Suppression des Doublons (2025-08-14)

#### 📎 Suivi complet des pièces jointes
- **Historique des ajouts** : Ajout de pièces jointes aux déclarations et événements maintenant tracé dans l'historique
- **Historique des suppressions** : Suppression de pièces jointes enregistrée avec nom du fichier supprimé
- **Signaux Django optimisés** : Gestionnaires `post_save` et `post_delete` pour les modèles `GapReportAttachment` et `GapAttachment`
- **Descriptions explicites** : Messages clairs du type "27 - Déclaration d'événement modifiée - Ajout de pièce jointe : document.pdf"

#### 🚫 Élimination des doublons d'historique
- **Problème résolu** : Plus de doublons lors des modifications de pièces jointes ou personnes présentes
- **Système de prévention centralisé** : Mécanisme global `set_specific_modification_in_progress()` pour coordonner les signaux
- **Signaux coordonnés** : Synchronisation entre signaux M2M (`involved_users`) et signaux génériques (`post_save`)
- **Solution technique élégante** : Flag temporaire thread-local pour éviter les entrées d'historique concurrentes

#### 🔧 Architecture des signaux améliorée
- **Fonctions utilitaires globales** : `set_specific_modification_in_progress()` et `is_specific_modification_in_progress()`
- **Vue optimisée** : Définition du flag de prévention AVANT `form.save()` pour coordination parfaite des signaux
- **Signaux M2M intelligents** : Respect du flag existant sans le redéfinir si déjà configuré par la vue
- **Code nettoyé** : Suppression des logs de debug et fonctions inutilisées après validation

#### 🎯 Expérience utilisateur améliorée
- **Historique propre** : Une seule entrée par modification, plus de confusion avec les doublons
- **Traçabilité exhaustive** : Toutes les modifications (champs, pièces jointes, personnes présentes) parfaitement enregistrées
- **Performance maintenue** : Solution optimisée sans impact sur les performances des signaux Django
- **Maintenance simplifiée** : Architecture centralisée facile à étendre pour de nouveaux types de modifications

### v2.12.0 - Protection des Champs et Historique Amélioré (2025-08-14)

#### 🔒 Protection des champs lors d'édition avec écarts existants
- **Champ Service désactivé** : Le service ne peut plus être modifié quand des écarts sont associés à la déclaration
- **Champ Source d'audit désactivé** : La source d'audit ne peut plus être modifiée quand des écarts sont associés
- **Affichage des valeurs actuelles** : Les champs désactivés affichent correctement les valeurs sélectionnées initialement
- **Style visuel cohérent** : Champs grisés avec curseur "not-allowed" pour indiquer qu'ils ne sont pas modifiables
- **Messages d'aide explicites** : Indication claire que les champs ne peuvent pas être modifiés car des écarts existent

#### 📝 Historique des modifications enrichi pour les personnes impliquées
- **Traçabilité complète** : Ajout et suppression de "personnes présentes" maintenant enregistrés dans l'historique
- **Descriptions explicites** : "Ajout de personnes présentes : [Nom Prénom]" et "Suppression de personnes présentes : [Nom Prénom]"
- **Signal M2M optimisé** : Gestion des relations ManyToMany avec capture des changements en temps réel
- **Données JSON enrichies** : Informations complètes des utilisateurs impliqués dans les champs avant/après de l'historique

#### 🛡️ Intégrité des données renforcée
- **Validation côté serveur** : Impossible de modifier service ou source d'audit via manipulation de formulaire
- **Cohérence des écarts** : Garantit que les écarts restent cohérents avec leur déclaration d'origine
- **Protection contre les erreurs** : Empêche les modifications accidentelles qui rendraient les écarts incohérents
- **Architecture robuste** : Logique centralisée dans le formulaire Django avec validation en double sécurité

#### 🔧 Améliorations techniques
- **Queryset intelligent** : Inclusion automatique des valeurs actuelles même si elles ne sont plus dans le filtrage
- **Templates épurés** : Utilisation directe du système de formulaires Django plutôt que des templates partiels complexes
- **Signaux optimisés** : Gestion propre des changements M2M avec `set_current_user` pour traçabilité
- **Code nettoyé** : Suppression du debug et consolidation de la logique de protection des champs

### v2.11.1 - Correction Affichage Écarts Impliqués (2025-08-14)

#### 🐛 Correction critique du filtrage des écarts
- **Bug Django QuerySet résolu** : Les écarts auxquels un utilisateur était impliqué n'apparaissaient pas dans la vue par défaut
- **Problème Prefetch corrigé** : Suppression du `Prefetch` sur `involved_users` qui causait des conflits avec les filtres Django
- **Ordre des filtres optimisé** : Application du filtre `is_gap=True/False` en premier pour éviter les corruptions de QuerySet
- **Logique de pré-remplissage corrigée** : Suppression du pré-remplissage automatique des champs dans la vue par défaut qui causait un sur-filtrage

#### 🎯 Amélioration de l'expérience utilisateur
- **Vue par défaut fonctionnelle** : Les utilisateurs voient maintenant correctement tous les écarts auxquels ils sont impliqués
- **Visibilité des écarts annulés** : Les écarts annulés sont désormais visibles aux utilisateurs impliqués (pas seulement au déclarant)
- **Détection de formulaire améliorée** : Meilleure distinction entre vue par défaut et formulaire soumis avec les checkboxes

#### 🔧 Corrections techniques
- **QuerySet propre** : Restructuration complète de la logique de filtrage pour éviter les interactions imprévisibles
- **Méthode `is_visible_to_user()` améliorée** : Prise en compte des utilisateurs impliqués pour tous les statuts d'écart
- **Architecture de filtrage simplifiée** : Suppression des optimisations complexes qui causaient des bugs subtils

### v2.11.0 - Filtrage Intelligent des Sources d'Audit (2025-08-14)

#### 🎯 Filtrage des sources d'audit par validateurs
- **Filtrage automatique initial** : Seules les sources d'audit ayant des validateurs configurés pour le service apparaissent dans les formulaires
- **Filtrage dynamique HTMX** : Mise à jour automatique des sources disponibles lors du changement de service
- **Messages informatifs** : Indication claire quand aucune source n'est disponible pour un service donné
- **Cohérence formulaires** : Système unifié entre formulaire complet et modal de déclaration

#### 🔄 Amélioration de l'expérience utilisateur
- **Prévention des erreurs** : Impossible de créer des déclarations avec des sources non-validables
- **Template partiel centralisé** : Composant réutilisable `audit_sources_field.html` pour maintenir la cohérence
- **Intégration seamless** : Fonctionnement identique dans les deux modes de saisie (page complète et modal HTMX)
- **Performance optimisée** : Filtrage côté serveur pour éviter le chargement de données inutiles

#### 🛡️ Sécurisation du workflow
- **Validation préventive** : Empêche la création d'écarts qui ne pourraient pas être validés
- **Filtrage par service utilisateur** : Sources filtrées automatiquement selon le service par défaut de l'utilisateur connecté
- **Messages d'aide simplifiés** : Suppression du lien vers la gestion workflow dans les messages d'erreur
- **Architecture consolidée** : Vue unique `get_audit_sources_field` pour gérer tous les cas de filtrage

#### 🔧 Améliorations techniques
- **Templates partiels HTMX** : Réutilisation du composant entre formulaire complet et modal
- **Filtrage en cascade** : Service → ValidateurService → AuditSource pour garantir la cohérence
- **JavaScript conditionnel** : Appel à `loadGapTypesReliable()` uniquement dans le contexte modal
- **Requêtes optimisées** : Utilisation de `values_list().distinct()` pour des performances maximales

### v2.10.0 - Interface Utilisateur Améliorée et Notifications Optimisées (2025-08-13)

#### 🎨 Amélioration de l'affichage des notifications
- **Format standardisé** : Toutes les notifications suivent le format "Numéro - Action" (ex: "23.1 - Événement créé")
- **Historique des modifications structuré** : Affichage HTML enrichi avec séparation claire entre titre et détails
- **Style avant/après amélioré** : Puces, couleurs distinctives (rouge/vert), et mise en page structurée
- **Badge "notification traitée"** : Distinction visuelle entre actions directes et notifications traitées dans l'historique

#### 🚫 Suppression des notifications en double
- **Élimination des doublons de rejet** : Une seule notification conservée lors du rejet d'écart (format du ValidationService)
- **Filtrage des notifications validateur** : Les validateurs ne reçoivent plus de notifications pour leurs propres actions
- **Notifications ciblées** : Seul le déclarant reçoit les notifications pertinentes, pas l'auteur des modifications

#### 🎯 Repositionnement des boutons de validation
- **Validation en bas de page** : Boutons approuver/rejeter déplacés sous le contenu de l'écart pour workflow logique
- **Interface dédiée** : Section "Actions de validation" avec cartes colorées et champs de commentaires agrandis
- **Design cohérent** : Fond vert pour approbation, fond rouge pour rejet avec bordures assorties

#### 🧹 Optimisations d'interface
- **Suppression du popup de déconnexion** : Plus de message "Vous avez été déconnecté avec succès"
- **Cache intelligent du dashboard** : Actualisation automatique des notifications après navigation
- **Affichage des pièces jointes corrigé** : Nom descriptif affiché au lieu du chemin technique
- **Compact vertical** : Espacement réduit dans l'historique avec timestamps alignés à droite

#### 🔧 Améliorations techniques
- **Gestion du cache navigateur** : Headers anti-cache et rechargement intelligent via JavaScript
- **Rendu HTML sécurisé** : Utilisation du filtre `|safe` pour l'affichage enrichi des modifications
- **Code nettoyé** : Suppression de la logique JavaScript inutile et simplification des templates

### v2.7.0 - Validation de Statut Restrictive et Historique Complet (2025-08-11)

#### 🔒 Sécurité et Permissions Renforcées
- **Validation niveau maximum uniquement** : Seuls les validateurs du niveau le plus élevé peuvent modifier le statut des écarts
- **Contrôle d'accès granulaire** : Validation du niveau de l'utilisateur par rapport au niveau maximum configuré pour chaque service/source d'audit
- **Messages d'erreur contextuels** : Distinction claire entre "pas validateur" et "niveau insuffisant"
- **Protection administrative maintenue** : Super Administrateurs et Administrateurs conservent tous les droits

#### 📊 Historique des Validations Enrichi
- **Changements de statut tracés** : Les modifications directes de statut apparaissent dans l'historique des validations
- **Distinction visuelle** : Interface adaptée pour distinguer validations classiques et changements directs
- **Commentaires automatiques** : Génération automatique de commentaires explicites pour les changements directs
- **Mapping intelligent** : Correspondance automatique statut → action de validation (retained → approved, rejected → rejected, closed → approved)

#### 🎯 Améliorations UX/UI
- **Template amélioré** : Affichage "a modifié le statut directement" pour les changements directs vs "a approuvé/rejeté"
- **Historique unifié** : Un seul endroit pour voir toutes les actions de validation, directes ou via workflow
- **Niveau de validation visible** : Affichage du niveau de validation dans tous les cas
- **Gestion des conflits** : Utilisation d'update_or_create pour éviter les doublons par niveau

#### 🔧 Améliorations Techniques
- **Logique centralisée** : Même règle de validation appliquée dans gap_detail et change_gap_status
- **Transactions atomiques** : Création simultanée de l'historique général et de validation
- **Optimisation des requêtes** : Utilisation d'agregation Max() pour déterminer les niveaux

### v2.6.0 - Architecture Épurée et Documentation Consolidée (2025-08-10)

#### 🧹 Nettoyage des fichiers
- **Suppression des fichiers de test** : `test_optimizations.py` et `test_urls.py` supprimés
- **Consolidation de la documentation** : Toutes les informations de développement et déploiement intégrées dans README.md
- **Suppression des fichiers .md redondants** : `deployment_guide.md`, `README_OPTIMIZATIONS.md`, `QUICK_START.md` supprimés
- **Architecture épurée** : Réduction du nombre de fichiers tout en conservant toutes les informations essentielles

#### 📖 Documentation unifiée
- **Guide développeur complet** : Instructions d'installation, développement et déploiement dans un seul fichier
- **Section déploiement production détaillée** : Configuration PostgreSQL, Redis, Nginx, Gunicorn
- **Optimisations de performance documentées** : Cache distribué, pagination, transactions concurrentielles
- **Tests de performance intégrés** : Validation pour 400+ utilisateurs concurrents

#### 🎯 Amélioration de la maintenabilité
- **README.md central** : Point d'entrée unique pour toute la documentation technique
- **Variables d'environnement clarifiées** : Configuration simplifiée avec `.env.example`
- **Commandes de maintenance consolidées** : Backup, monitoring, surveillance dans une section dédiée

### v2.8.0 - Interface d'Administration Enrichie et Suppression de Masse (2025-08-13)

#### 🗑️ Suppression de masse sécurisée
- **Suppression de toutes les notifications** : Bouton de suppression de masse avec confirmation multi-niveaux
- **Suppression de tout l'historique** : Fonctionnalité équivalente pour l'historique des modifications
- **Interface de confirmation robuste** : Page de confirmation avec statistiques détaillées et saisie manuelle obligatoire
- **Protection par mot-clé** : Saisie de "SUPPRIMER TOUT" ou "SUPPRIMER HISTORIQUE" obligatoire pour confirmer
- **Double confirmation JavaScript** : Protection supplémentaire avec confirmation navigateur

#### 🎨 Design cohérent et accessible
- **Boutons stylisés** : Boutons de suppression de masse avec style Django standard mais couleur rouge
- **Thème sombre adapté** : Couleurs optimisées pour la lisibilité dans l'interface d'administration
- **Statistiques visuelles** : Tableaux détaillés montrant le nombre d'éléments par type/action avant suppression
- **Messages d'état clairs** : Feedback utilisateur avec compteurs précis et détails de suppression

#### 🔒 Sécurité administrative renforcée
- **Boutons "Ajouter" désactivés** : Empêche la création manuelle de notifications et d'historique (générés automatiquement)
- **Permissions granulaires** : Seuls les superutilisateurs peuvent effectuer les suppressions de masse
- **Logging administratif** : Enregistrement détaillé des suppressions massives dans les logs Django
- **URLs personnalisées** : Routes dédiées `/delete_all/` pour chaque type de suppression

#### 🛠️ Améliorations techniques
- **Templates personnalisés** : `change_list.html` et `delete_all_confirmation.html` pour chaque modèle
- **Méthodes admin étendues** : `get_urls()` et vues personnalisées pour gérer les suppressions de masse
- **Gestion des erreurs** : Protection contre les suppressions sur données vides avec messages informatifs
- **Architecture modulaire** : Organisation des templates dans `admin/notifications/` et `admin/historique/`

### v2.9.0 - Système de Filtrage Actif/Inactif Complet (2025-08-13)

#### 🎯 Filtrage actif/inactif étendu
- **Sources d'audit (3.1)** : Ajout du champ `is_active` avec filtrage automatique dans les formulaires
- **Types d'événement (3.3)** : Ajout du champ `is_active` avec filtrage automatique dans les formulaires
- **Processus SMI (3.2)** : Filtrage actif/inactif existant optimisé avec icônes cohérentes
- **Cohérence visuelle** : Icônes ✓/✗ standardisées pour tous les modèles dans l'admin Django

#### 🔄 Synchronisation automatique multi-session
- **Signaux Django** : Invalidation automatique du cache lors des modifications (`post_save`/`post_delete`)
- **Cache intelligent** : Maintien des performances avec mise à jour temps réel entre toutes les sessions
- **Headers anti-cache** : Prévention du cache navigateur pour les données dynamiques (`Cache-Control`, `Pragma`, `Expires`)
- **API HTMX optimisée** : Requêtes sans cache pour les listes déroulantes dynamiques

#### 🗃️ Préservation des données existantes
- **Non-destructif** : Les éléments inactifs restent liés aux déclarations/écarts existants
- **Filtrage intelligent** : Seuls les nouveaux formulaires filtrent les éléments inactifs
- **Intégrité référentielle** : Aucune rupture des relations existantes lors de la désactivation

#### 🔧 Architecture technique avancée
- **Signaux automatisés** : `@receiver(post_save/post_delete)` pour AuditSource, Process, GapType
- **Cache multi-niveaux** : Cache serveur + invalidation globale + headers navigateur
- **Migrations sécurisées** : Ajout des champs `is_active` avec valeurs par défaut et index
- **Formulaires dynamiques** : Filtrage en temps réel via HTMX avec gestion d'erreur robuste

### v2.5.1 - Corrections Interface et Suppression Services (2025-08-10)

#### 🐛 Corrections critiques
- **Suppression de services fonctionnelle** : Correction du problème UnboundLocalError dans la suppression des services
- **Template de confirmation corrigé** : Réparation de l'URL service_delete_confirm manquante
- **Interface validateurs optimisée** : Suppression de la colonne "Rôles de Validation" redondante, ajout de la colonne Email manquante
- **Import des modules nettoyé** : Imports render_to_string et get_token déplacés au niveau global pour éviter les erreurs de scope

#### 🎯 Améliorations UX
- **Liste validateurs simplifiée** : Colonnes optimales (Utilisateur, Matricule, Droits, Service, Email, Nb Rôles, Actions)
- **Suppression services fluide** : Système à deux étapes (confirmation → suppression) avec modales cohérentes
- **Gestion d'erreur robuste** : Messages d'erreur clairs pour contraintes de suppression (sous-services, utilisateurs, écarts)
- **Interface épurée** : Suppression du détail verbose des rôles au profit du nombre de rôles plus concis

---

**📝 Note importante**: Ce README.md doit être mis à jour avant chaque commit qui introduit des changements techniques, architecturaux ou de configuration.