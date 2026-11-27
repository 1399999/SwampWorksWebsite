from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', views.admin_index, name='admin'),
    path('admin/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/users/<int:user_id>/request-admin/', views.request_admin_role, name='request_admin_role'),
    path('admin/users/<int:user_id>/make-user/', views.make_regular_user, name='make_regular_user'),
    path('confirm-admin/<str:token>/', views.confirm_admin, name='confirm_admin'),
]