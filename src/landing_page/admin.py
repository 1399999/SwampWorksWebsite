from django.contrib import admin
from .models import Project, ProjectImage, ProjectMember, Idea, ClubMeeting, Contact


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_approved', 'admin_approved_by', 'created_at')
    list_filter = ('status', 'is_approved')
    inlines = [ProjectImageInline, ProjectMemberInline]


admin.site.register(Idea)
admin.site.register(ClubMeeting)
admin.site.register(Contact)