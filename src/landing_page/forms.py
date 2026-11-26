from django import forms
from django.forms import inlineformset_factory

from .models import Project, ProjectImage, ProjectMember, Idea, ClubMeeting, Contact


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """An image upload field that accepts several files at once."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        clean_one = super().clean
        if isinstance(data, (list, tuple)):
            return [clean_one(item, initial) for item in data]
        return [clean_one(data, initial)] if data else []


class ProjectForm(forms.ModelForm):
    """A member submitting a new project: at least one photo is required."""

    new_images = MultipleImageField(
        required=False,
        label='Photos',
        help_text='Select one or more photos.',
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Project title'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your project...'}),
            'technologies': forms.TextInput(attrs={'placeholder': 'Python, Pygame, Arduino'}),
        }

    def clean_new_images(self):
        images = self.cleaned_data.get('new_images') or []
        if not images:
            raise forms.ValidationError('Please upload at least one photo.')
        return images


class ProjectEditForm(ProjectForm):
    """An admin editing a project: adds status and photo removal; photos are optional."""

    delete_images = forms.ModelMultipleChoiceField(
        queryset=ProjectImage.objects.none(),
        required=False,
    )

    class Meta(ProjectForm.Meta):
        fields = ['title', 'description', 'technologies', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delete_images'].queryset = self.instance.images.all()
        self.fields['new_images'].label = 'Add more photos'

    def clean_new_images(self):
        return self.cleaned_data.get('new_images') or []


_member_widgets = {
    'name': forms.TextInput(attrs={'placeholder': 'Name'}),
    'role': forms.TextInput(attrs={'placeholder': 'Role'}),
}

ProjectMemberFormSet = inlineformset_factory(
    Project, ProjectMember, fields=('name', 'role'),
    extra=4, can_delete=False, widgets=_member_widgets,
)

EditMemberFormSet = inlineformset_factory(
    Project, ProjectMember, fields=('name', 'role'),
    extra=3, can_delete=True, widgets=_member_widgets,
)


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
            'name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'role': forms.TextInput(attrs={'placeholder': 'e.g. Secretary'}),
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
        }
