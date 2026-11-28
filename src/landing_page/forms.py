from django import forms
from django.contrib.auth import get_user_model
from django.forms import BaseInlineFormSet, inlineformset_factory

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

MEMBER_ROLE_CHOICES = [('Member', 'Member'), ('Leader', 'Leader')]


def user_name_choices():
    """Everyone with an account, by first and last name, for the team dropdown."""
    choices = [('', 'Select a person')]
    for user in get_user_model().objects.order_by('first_name', 'last_name', 'username'):
        choices.append((str(user.pk), user.get_full_name() or user.username))
    return choices


class NewMemberForm(forms.ModelForm):
    """A team member on a new project: pick a person from the user list and a role (Member or Leader)."""

    person = forms.ChoiceField(choices=[('', 'Select a person')])
    role = forms.ChoiceField(choices=MEMBER_ROLE_CHOICES, initial='Member')

    class Meta:
        model = ProjectMember
        fields = ('role',)

    def __init__(self, *args, name_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['person'].choices = name_choices or user_name_choices()
        # a blank extra row counts as untouched only if its role starts out as Member
        if not self.initial.get('role'):
            self.initial['role'] = 'Member'

    def clean_person(self):
        value = self.cleaned_data.get('person')
        if not value:
            return None
        return get_user_model().objects.get(pk=value)

    def save(self, commit=True):
        person = self.cleaned_data.get('person')
        if person:
            self.instance.user = person
            self.instance.name = person.get_full_name() or person.username
        return super().save(commit=commit)


class BaseNewMemberFormSet(BaseInlineFormSet):
    def get_form_kwargs(self, index):
        # look the users up once per page instead of once per row
        kwargs = super().get_form_kwargs(index)
        if not hasattr(self, '_name_choices'):
            self._name_choices = user_name_choices()
        kwargs['name_choices'] = self._name_choices
        return kwargs

    def clean(self):
        super().clean()
        leaders = 0
        people = []
        for form in self.forms:
            data = getattr(form, 'cleaned_data', None)
            if not data or not data.get('person'):
                continue
            people.append(data['person'].pk)
            if data.get('role') == 'Leader':
                leaders += 1
        if leaders > 1:
            raise forms.ValidationError('Only one team member can be the leader.')
        if len(people) != len(set(people)):
            raise forms.ValidationError('Each person can only be added to a project once.')


ProjectMemberFormSet = inlineformset_factory(
    Project, ProjectMember, form=NewMemberForm, formset=BaseNewMemberFormSet,
    extra=4, can_delete=False,
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