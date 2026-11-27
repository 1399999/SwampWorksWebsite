from django import template

from landing_page.models import Contact, Project

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    """Render a form field with extra CSS classes, e.g. {{ field|add_class:"form-control" }}."""
    existing = field.field.widget.attrs.get('class', '')
    classes = f"{existing} {css_class}".strip()
    return field.as_widget(attrs={'class': classes})


@register.simple_tag
def nav_projects():
    """Approved projects for the navbar menu: current projects first, then previous ones."""
    return Project.objects.filter(is_approved=True).order_by('-status', 'title')


@register.simple_tag
def officers():
    """The President and Vice President from the Contact data, for the footer."""
    found = []
    for role in ('President', 'Vice President'):
        person = Contact.objects.filter(role__iexact=role).order_by('pk').first()
        if person:
            found.append(person)
    return found