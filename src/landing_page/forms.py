from django import forms
from .models import Project
 
 
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['image', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your project...'}),
        }
