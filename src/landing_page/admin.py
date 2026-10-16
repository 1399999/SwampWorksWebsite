from django.contrib import admin
from .models import Project, Idea, ClubMeeting, Contact

# Register your models here.
admin.site.register(Project)
admin.site.register(Idea)
admin.site.register(ClubMeeting)
admin.site.register(Contact)