from django.contrib import admin
from .models import Project, Idea, ClubMeeting

# Register your models here.
admin.site.register(Project)
admin.site.register(Idea)
admin.site.register(ClubMeeting)