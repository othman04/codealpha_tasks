from django import forms

from .models import Project, ProjectMember




class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom du projet'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Description'}),
        }


class InviteMemberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': "Nom d'utilisateur"}),
    )
    role = forms.ChoiceField(
        choices=ProjectMember.ROLE_CHOICES[1:],
        widget=forms.Select(attrs={'class': 'form-input'}),
    )
