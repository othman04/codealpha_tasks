from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('project/create/', views.project_create, name='project_create'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('project/<int:pk>/invite/', views.invite_member, name='invite_member'),
]
