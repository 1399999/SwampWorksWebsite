from django import forms
from .models import Project, Idea, ClubMeeting, Contact


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


class MeetingForm(forms.ModelForm):
    class Meta:
        model = ClubMeeting
        fields = ['title', 'description', 'date', 'time']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional details...'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'role', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Secretary'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
        }