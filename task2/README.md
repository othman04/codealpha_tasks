# SocialNet — Réseau social Django

Application web de réseau social minimal développée avec Django.

## Fonctionnalités

- **Authentification** : inscription, connexion, déconnexion
- **Profil utilisateur** : photo, nom d'utilisateur, bio
- **Publications** : créer, afficher, modifier, supprimer
- **Interactions** : aimer, commenter, suivre/ne plus suivre

## Structure du projet

```
social_network/
├── accounts/       # Authentification et profils
├── posts/          # Publications
├── interactions/   # Likes, commentaires, abonnements
├── config/         # Configuration Django
├── templates/      # Templates HTML
├── static/         # CSS
└── manage.py
```

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
cd social_network
python manage.py migrate

# Lancer le serveur
python manage.py runserver
```

Accédez à l'application : http://127.0.0.1:8000/

## Routes principales

| URL | Description |
|-----|-------------|
| `/register` | Inscription |
| `/login` | Connexion |
| `/logout` | Déconnexion |
| `/feed` | Fil d'actualité |
| `/profile/<username>` | Profil utilisateur |
| `/profile/edit` | Modifier son profil |
| `/post/create` | Créer une publication |
| `/post/<id>` | Détail d'une publication |

## Modèles

- **User** (Django intégré) — username, email, password
- **Profile** — user, photo, bio
- **Post** — author, content, image, created_at
- **Comment** — user, post, content, created_at
- **Follow** — follower, following
- **Like** — user, post
