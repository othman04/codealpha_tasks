from django import forms

from projects.models import Project
from .models import Comment, Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'project', 'assigned_to', 'status', 'due_date')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Titre de la tâche'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'project': forms.Select(attrs={'class': 'form-input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'assigned_to', 'status', 'due_date')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Titre de la tâche'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'assigned_to': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Ajouter un commentaire...',
            }),
        }
