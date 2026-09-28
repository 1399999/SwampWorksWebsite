from django.urls import path, include
from . import views
 
app_name = 'landing_page'
 
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('projects/', views.projects, name='projects'),
    path('contact/', views.contact, name='contact'),
]
 