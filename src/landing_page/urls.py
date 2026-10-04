from django.urls import path, include
from . import views

app_name = 'landing_page'

urlpatterns = [
    path('', views.index, name='index'),
    path('meetings/<int:meeting_id>/delete/', views.delete_meeting, name='delete_meeting'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/status/', views.update_project_status, name='update_project_status'),
    path('ideas/', views.ideas, name='ideas'),
    path('contact/', views.contact, name='contact'),
]