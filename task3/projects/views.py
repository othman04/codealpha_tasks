from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.models import User

from notifications.utils import create_notification
from .forms import InviteMemberForm, ProjectForm
from .models import Project, ProjectMember


def is_project_member(user, project):
    return ProjectMember.objects.filter(project=project, user=user).exists()


@user_passes_test(lambda u: u.is_authenticated)
def dashboard(request):
    memberships = ProjectMember.objects.filter(user=request.user).select_related('project')
    projects = [m.project for m in memberships]
    return render(request, 'projects/dashboard.html', {'projects': projects})


@user_passes_test(lambda u: u.is_authenticated)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            ProjectMember.objects.create(
                project=project,
                user=request.user,
                role=ProjectMember.ROLE_OWNER,
            )
            messages.success(request, f'Projet "{project.name}" créé avec succès.')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Créer un projet'})


@user_passes_test(lambda u: u.is_authenticated)
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not is_project_member(request.user, project):
        messages.error(request, "Vous n'avez pas accès à ce projet.")
        return redirect('projects:dashboard')

    tasks_todo = project.tasks.filter(status='todo')
    tasks_in_progress = project.tasks.filter(status='in_progress')
    tasks_done = project.tasks.filter(status='done')
    members = project.members.select_related('user')
    invite_form = InviteMemberForm()

    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks_todo': tasks_todo,
        'tasks_in_progress': tasks_in_progress,
        'tasks_done': tasks_done,
        'members': members,
        'invite_form': invite_form,
        'is_owner': project.owner == request.user,
    })


@user_passes_test(lambda u: u.is_authenticated)
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        messages.error(request, 'Seul le propriétaire peut modifier le projet.')
        return redirect('projects:project_detail', pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projet mis à jour.')
            return redirect('projects:project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Modifier le projet'})


@user_passes_test(lambda u: u.is_authenticated)
def invite_member(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        messages.error(request, 'Seul le propriétaire peut inviter des membres.')
        return redirect('projects:project_detail', pk=pk)

    if request.method == 'POST':
        form = InviteMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            role = form.cleaned_data['role']
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, f"Utilisateur '{username}' introuvable.")
                return redirect('projects:project_detail', pk=pk)

            if ProjectMember.objects.filter(project=project, user=user).exists():
                messages.warning(request, f'{username} est déjà membre du projet.')
            else:
                ProjectMember.objects.create(project=project, user=user, role=role)
                create_notification(
                    user,
                    f'Vous avez été invité au projet "{project.name}".',
                )
                messages.success(request, f'{username} a été ajouté au projet.')
    return redirect('projects:project_detail', pk=pk)
