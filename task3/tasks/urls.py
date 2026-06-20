from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/<int:pk>/status/', views.task_status_update, name='task_status_update'),
]
