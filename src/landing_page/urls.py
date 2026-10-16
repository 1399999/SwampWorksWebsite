from django.urls import path, include
from . import views

app_name = 'landing_page'

urlpatterns = [
    path('', views.index, name='index'),
    path('meetings/<int:meeting_id>/delete/', views.delete_meeting, name='delete_meeting'),
    path('about/', views.index, name='about'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/status/', views.update_project_status, name='update_project_status'),
    path('projects/<int:project_id>/approve/', views.approve_project, name='approve_project'),
    path('projects/<int:project_id>/reject/', views.reject_project, name='reject_project'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('ideas/<int:idea_id>/delete/', views.delete_idea, name='delete_idea'),
    path('ideas/', views.ideas, name='ideas'),
    path('contact/', views.contact, name='contact'),
    path('contact/<int:contact_id>/delete/', views.delete_contact, name='delete_contact'),
]