from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from notifications.utils import create_notification
from projects.models import Project, ProjectMember
from tasks.models import Comment, Task


class Command(BaseCommand):
    help = 'Crée des données de démonstration'

    def handle(self, *args, **options):
        if User.objects.filter(username='alice').exists():
            self.stdout.write('Données de démo déjà présentes.')
            return

        alice = User.objects.create_user('alice', 'alice@example.com', 'demo1234')
        bob = User.objects.create_user('bob', 'bob@example.com', 'demo1234')

        project = Project.objects.create(
            name='Projet Alpha',
            description='Application de gestion de projet collaborative.',
            owner=alice,
        )
        ProjectMember.objects.create(project=project, user=alice, role=ProjectMember.ROLE_OWNER)
        ProjectMember.objects.create(project=project, user=bob, role=ProjectMember.ROLE_MEMBER)

        task1 = Task.objects.create(
            title='Task 1',
            description='Configurer le backend Django',
            project=project,
            assigned_to=alice,
            status=Task.STATUS_TODO,
        )
        task2 = Task.objects.create(
            title='Task 2',
            description='Créer les templates Kanban',
            project=project,
            assigned_to=bob,
            status=Task.STATUS_IN_PROGRESS,
        )
        task3 = Task.objects.create(
            title='Task 3',
            description='Mettre en place les notifications',
            project=project,
            assigned_to=alice,
            status=Task.STATUS_DONE,
        )
        task4 = Task.objects.create(
            title='Task 4',
            description='Tests et documentation',
            project=project,
            assigned_to=bob,
            status=Task.STATUS_TODO,
        )

        Comment.objects.create(task=task2, user=alice, content='Bon travail sur le design !')
        create_notification(bob, 'Vous avez été assigné à la tâche "Task 2".')

        self.stdout.write(self.style.SUCCESS('Données de démo créées.'))
        self.stdout.write('Comptes : alice / demo1234  |  bob / demo1234')
