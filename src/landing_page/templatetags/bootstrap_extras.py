from django import template

from landing_page.models import Project

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
