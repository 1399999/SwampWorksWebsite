from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_index, name='admin'),
    path('admin/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
]