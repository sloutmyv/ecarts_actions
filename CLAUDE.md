# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EcartsActions est une application Django moderne utilisant:
- **Frontend**: Tailwind CSS + HTMX + Alpine.js
- **Backend**: Django 5.2.4
- **Base de données**: SQLite (développement)

## Environment Setup

- **Python Version**: 3.12.3 (managed via pyenv)
- **Virtual Environment**: Located in `venv/` directory
- **Framework**: Django 5.2.4
- **Dependencies**: Listed in `requirements.txt`

## Development Commands

- **Activate virtual environment**: `source venv/bin/activate`
- **Install dependencies**: `pip install -r requirements.txt`
- **Run development server**: `python manage.py runserver`
- **Create migrations**: `python manage.py makemigrations`
- **Apply migrations**: `python manage.py migrate`
- **Create superuser**: `python manage.py createsuperuser`
- **Collect static files**: `python manage.py collectstatic`

## Project Structure

```
ecarts_actions/
├── ecarts_actions/          # Configuration Django
│   ├── settings.py         # Configuration principale
│   ├── urls.py            # URLs racine
│   └── wsgi.py            # Configuration WSGI
├── core/                   # Application principale
├── templates/              # Templates Django
│   └── base.html          # Template de base avec Tailwind/HTMX/Alpine
├── static/                 # Fichiers statiques
│   ├── css/               # CSS personnalisés
│   └── js/                # JavaScript personnalisés
├── venv/                  # Environnement virtuel
├── manage.py              # CLI Django
└── requirements.txt       # Dépendances Python
```

## Frontend Stack

- **Tailwind CSS**: Framework CSS utility-first (CDN)
- **HTMX**: Interactions AJAX sans JavaScript complexe
- **Alpine.js**: Réactivité côté client légère
- **Django Compressor**: Compression des assets statiques

## Development Guidelines

- Utiliser HTMX pour les interactions AJAX
- Implémenter des modales HTMX pour les formulaires
- Créer des split buttons pour les actions d'édition/suppression
- Suivre les conventions Tailwind CSS pour le styling
- Utiliser Alpine.js pour l'interactivité côté client