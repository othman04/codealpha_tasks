from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from notifications.utils import create_notification
from projects.models import Project, ProjectMember
from .forms import CommentForm, TaskCreateForm, TaskForm
from .models import Task


def can_access_task(user, task):
    return ProjectMember.objects.filter(project=task.project, user=user).exists()


def get_project_members_queryset(project):
    member_ids = ProjectMember.objects.filter(project=project).values_list('user', flat=True)
    from django.contrib.auth.models import User
    return User.objects.filter(pk__in=member_ids)


@user_passes_test(lambda u: u.is_authenticated)
def task_create(request):
    project_id = request.GET.get('project')
    project = None
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
        if not ProjectMember.objects.filter(project=project, user=request.user).exists():
            messages.error(request, "Vous n'avez pas accès à ce projet.")
            return redirect('projects:dashboard')

    if request.method == 'POST':
        form = TaskCreateForm(request.POST)
        post_project_id = request.POST.get('project_id') or project_id
        post_project = get_object_or_404(Project, pk=post_project_id)
        form.fields['assigned_to'].queryset = get_project_members_queryset(post_project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = post_project
            task.save()
            if task.assigned_to:
                create_notification(
                    task.assigned_to,
                    f'Vous avez été assigné à la tâche "{task.title}".',
                )
            messages.success(request, 'Tâche créée avec succès.')
            return redirect('projects:project_detail', pk=task.project.pk)
    else:
        form = TaskCreateForm()
        if project:
            form.fields['assigned_to'].queryset = get_project_members_queryset(project)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Créer une tâche',
        'project': project,
    })


@user_passes_test(lambda u: u.is_authenticated)
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not can_access_task(request.user, task):
        messages.error(request, "Vous n'avez pas accès à cette tâche.")
        return redirect('projects:dashboard')

    members_qs = get_project_members_queryset(task.project)
    comment_form = CommentForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'comment':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.user = request.user
                comment.save()
                notify_users = set()
                if task.assigned_to and task.assigned_to != request.user:
                    notify_users.add(task.assigned_to)
                if task.project.owner != request.user:
                    notify_users.add(task.project.owner)
                for user in notify_users:
                    create_notification(
                        user,
                        f'Nouveau commentaire sur "{task.title}" par {request.user.username}.',
                    )
                messages.success(request, 'Commentaire ajouté.')
                return redirect('tasks:task_detail', pk=pk)
        elif action == 'update':
            old_assignee = task.assigned_to
            old_status = task.status
            form = TaskForm(request.POST, instance=task)
            form.fields['assigned_to'].queryset = members_qs
            if form.is_valid():
                updated_task = form.save()
                if updated_task.assigned_to and updated_task.assigned_to != old_assignee:
                    create_notification(
                        updated_task.assigned_to,
                        f'Vous avez été assigné à la tâche "{updated_task.title}".',
                    )
                if updated_task.status != old_status and updated_task.assigned_to:
                    create_notification(
                        updated_task.assigned_to,
                        f'Statut de "{updated_task.title}" changé en {updated_task.get_status_display()}.',
                    )
                messages.success(request, 'Tâche mise à jour.')
                return redirect('tasks:task_detail', pk=pk)

    form = TaskForm(instance=task)
    form.fields['assigned_to'].queryset = members_qs

    return render(request, 'tasks/task_detail.html', {
        'task': task,
        'form': form,
        'comment_form': comment_form,
        'comments': task.comments.select_related('user'),
    })


@user_passes_test(lambda u: u.is_authenticated)
def task_status_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not can_access_task(request.user, task):
        messages.error(request, "Vous n'avez pas accès à cette tâche.")
        return redirect('projects:dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Task.STATUS_CHOICES]
        if new_status in valid_statuses:
            old_status = task.status
            task.status = new_status
            task.save()
            if task.assigned_to and old_status != new_status:
                create_notification(
                    task.assigned_to,
                    f'Statut de "{task.title}" changé en {task.get_status_display()}.',
                )
            messages.success(request, f'Statut mis à jour : {task.get_status_display()}.')

    return redirect('projects:project_detail', pk=task.project.pk)
