"""
URL configuration for the notification app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('read/<int:pk>/', views.read_notification, name='read_notification'),
]