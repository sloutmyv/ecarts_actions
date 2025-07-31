# Git Hooks - EcartsActions

## Vue d'ensemble

Ce projet utilise des Git hooks pour automatiser certaines vérifications et rappels avant les commits, garantissant ainsi la qualité et la cohérence de la documentation.

## Hooks configurés

### 1. Pre-commit hook

**Fichier**: `.git/hooks/pre-commit`

**Objectif**: Vérifier que la documentation est à jour avant chaque commit

**Fonctionnalités**:
- ✅ Analyse des fichiers modifiés (Python, HTML, configuration)
- ✅ Vérification de l'âge des fichiers de documentation
- ✅ Recommandations de mise à jour de README.md et MANUEL.md
- ✅ Vérifications Django (migrations, etc.)
- ✅ Possibilité de forcer le commit avec avertissement

**Déclenchement**: Automatique avant chaque `git commit`

### 2. Prepare-commit-msg hook

**Fichier**: `.git/hooks/prepare-commit-msg`

**Objectif**: Fournir un template de message de commit standardisé

**Fonctionnalités**:
- ✅ Template avec format recommandé
- ✅ Liste des types de commits disponibles
- ✅ Exemples concrets
- ✅ Checklist de vérification
- ✅ Scopes suggérés pour le projet

**Déclenchement**: Automatique à l'ouverture de l'éditeur de commit

## Installation des hooks

Les hooks sont automatiquement créés lors de la configuration du projet. Si vous devez les réinstaller :

```bash
# Rendre les hooks exécutables
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/prepare-commit-msg
```

## Utilisation

### Workflow normal

1. **Faire des modifications** dans le code
2. **Ajouter les fichiers**: `git add .`
3. **Commiter**: `git commit`
   - Le pre-commit hook s'exécute automatiquement
   - Le template de message s'ouvre dans l'éditeur
4. **Suivre les recommandations** si nécessaire

### Exemple de session

```bash
$ git add core/views.py templates/core/item_list.html
$ git commit

🔍 Vérification avant commit...
📊 Analyse des changements:
   • Fichiers Python/HTML modifiés: 2
   • Fichiers de configuration modifiés: 1
   • README.md modifié il y a: 3 jour(s)
   • MANUEL.md modifié il y a: 1 jour(s)

⚠️  Des fichiers de configuration ont été modifiés
⚠️  Des fichiers techniques ont été modifiés mais README.md n'a pas été mis à jour aujourd'hui

📝 RECOMMANDATION - Mise à jour de la documentation suggérée:
   • README.md - Vérifiez si les changements techniques nécessitent une mise à jour
   • MANUEL.md - Vérifiez si les changements affectent l'expérience utilisateur

Voulez-vous continuer le commit sans mettre à jour la documentation ? (y/N)
```

### Bypass des hooks (déconseillé)

Si nécessaire, vous pouvez bypasser les hooks :

```bash
# Bypasser tous les hooks
git commit --no-verify

# Ou utiliser l'alias
git commit -n
```

⚠️ **Attention**: Cette pratique est déconseillée car elle peut conduire à une documentation obsolète.

## Personnalisation

### Modifier le pre-commit hook

Éditez `.git/hooks/pre-commit` pour :
- Ajouter de nouvelles vérifications
- Modifier les critères de mise à jour
- Changer les messages d'avertissement

### Modifier le template de commit

Éditez `.git/hooks/prepare-commit-msg` pour :
- Ajouter de nouveaux types de commits
- Modifier les scopes disponibles
- Personnaliser la checklist

## Dépannage

### Le hook ne s'exécute pas

```bash
# Vérifier les permissions
ls -la .git/hooks/pre-commit
# Doit afficher: -rwxr-xr-x

# Rendre exécutable si nécessaire
chmod +x .git/hooks/pre-commit
```

### Erreur dans le hook

```bash
# Tester le hook manuellement
.git/hooks/pre-commit

# Vérifier la syntaxe bash
bash -n .git/hooks/pre-commit
```

### Désactiver temporairement

```bash
# Renommer pour désactiver
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# Réactiver
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## Bonnes pratiques

### Pour les développeurs

1. **Respecter les recommendations** du pre-commit hook
2. **Mettre à jour la documentation** régulièrement
3. **Utiliser le template de commit** fourni
4. **Tester les hooks** après modification

### Pour les administrateurs

1. **Former l'équipe** à l'utilisation des hooks
2. **Maintenir les hooks** à jour selon l'évolution du projet
3. **Documenter les changements** dans ce fichier
4. **Surveiller** que les hooks sont bien utilisés

## Historique des modifications

| Date | Modification | Auteur |
|------|-------------|---------|
| 2024-XX-XX | Création des hooks pre-commit et prepare-commit-msg | Équipe Dev |

---

**Note**: Ce fichier fait partie de la documentation technique et doit être maintenu à jour avec les modifications des hooks.