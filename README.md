# EcartsActions - Guide Développeur

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture technique](#architecture-technique)
- [Installation et configuration](#installation-et-configuration)
- [Structure du projet](#structure-du-projet)
- [Stack technologique](#stack-technologique)
- [Conventions de développement](#conventions-de-développement)
- [Workflows de développement](#workflows-de-développement)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Maintenance](#maintenance)

## 🎯 Vue d'ensemble

EcartsActions est une application web moderne de gestion d'éléments/tâches construite avec Django et une stack frontend moderne privilégiant les interactions fluides sans rechargement de page.

### Objectifs du projet
- Interface utilisateur moderne et responsive
- Interactions fluides sans rechargement de page
- Composants réactifs côté client
- Modales pour les formulaires de création/modification
- Split buttons pour les actions combinées

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
Database (SQLite/PostgreSQL)
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

```
ecarts_actions/
├── 📁 ecarts_actions/          # Configuration Django
│   ├── settings.py            # ⚙️ Configuration principale
│   ├── urls.py               # 🔗 URLs racine
│   ├── wsgi.py               # 🚀 Configuration WSGI
│   └── asgi.py               # 🚀 Configuration ASGI
├── 📁 core/                   # 🎯 Application principale
│   ├── models.py             # 🗃️ Modèles de données
│   ├── views.py              # 👁️ Logique métier
│   ├── forms.py              # 📝 Formulaires Django
│   ├── urls.py               # 🔗 URLs de l'app
│   ├── admin.py              # 🔧 Configuration admin
│   └── migrations/           # 📦 Migrations DB
├── 📁 templates/              # 🎨 Templates Django
│   ├── base.html             # 🏠 Template de base
│   └── core/                 # 📁 Templates de l'app core
│       ├── item_list.html    # 📋 Liste des éléments
│       ├── item_form_modal.html  # 📝 Formulaire modal
│       └── item_row.html     # 📄 Ligne d'élément
├── 📁 static/                 # 🎭 Fichiers statiques
│   ├── css/                  # 🎨 CSS personnalisés
│   ├── js/                   # ⚡ JavaScript personnalisés
│   └── images/               # 🖼️ Images
├── 📁 venv/                   # 🐍 Environnement virtuel
├── manage.py                 # 🛠️ CLI Django
├── requirements.txt          # 📦 Dépendances Python
├── README.md                 # 📖 Documentation développeur
├── MANUEL.md                 # 📋 Manuel utilisateur
└── CLAUDE.md                 # 🤖 Guide Claude Code
```

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

### Conventions Python/Django
- **PEP 8**: Style guide Python standard
- **Django Conventions**: Nommage des modèles, vues, URLs
- **Docstrings**: Documentation des fonctions et classes

### Conventions Frontend
- **Tailwind Classes**: Utiliser les classes Tailwind plutôt que du CSS custom
- **HTMX Attributes**: Préfixer avec `hx-` et documenter les interactions
- **Alpine.js**: Utiliser `x-data`, `x-show`, etc. avec parcimonie

### Conventions de nommage
```python
# Modèles : PascalCase
class Item(models.Model):
    pass

# Vues : snake_case
def item_create(request):
    pass

# URLs : kebab-case
path('items/create/', views.item_create, name='item-create')

# Templates : snake_case
item_form_modal.html

# CSS Classes : kebab-case (Tailwind)
class="bg-blue-500 hover:bg-blue-700"
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