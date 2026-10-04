from django import forms
from .models import Project, Idea


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your project...'}),
        }


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share a project idea...'}),
        }