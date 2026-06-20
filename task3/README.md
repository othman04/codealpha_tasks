# Project Manager - Outil de gestion de projet Django

Application collaborative de gestion de projet (style Trello/Asana) avec tableaux Kanban, assignation de tâches, commentaires et notifications.

## Fonctionnalités

- **Authentification** : inscription, connexion, déconnexion
- **Projets** : création, modification, invitation de membres
- **Tâches** : création, assignation, changement de statut (À faire / En cours / Terminée)
- **Collaboration** : commentaires sur les tâches
- **Notifications** : alertes pour assignations, commentaires et changements de statut

## Structure

```
project_manager/
├── accounts/       # Authentification
├── projects/       # Projets et membres
├── tasks/          # Tâches et commentaires
├── notifications/  # Notifications
├── config/         # Configuration Django
├── templates/      # Templates HTML
└── static/         # CSS
```

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Accédez à http://127.0.0.1:8000/

## Pages

| URL | Description |
|-----|-------------|
| `/dashboard/` | Tableau de bord des projets |
| `/project/create/` | Créer un projet |
| `/project/<id>/` | Tableau Kanban du projet |
| `/task/create/` | Créer une tâche |
| `/task/<id>/` | Détail et commentaires d'une tâche |
| `/notifications/` | Liste des notifications |

## Utilisation

1. Créez un compte via **S'inscrire**
2. Créez un projet depuis le tableau de bord
3. Invitez des membres par leur nom d'utilisateur
4. Ajoutez des tâches et déplacez-les entre les colonnes Kanban
5. Commentez et assignez des tâches — les membres concernés recevront des notifications
