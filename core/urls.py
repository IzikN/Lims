from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('lab-manager/dashboard/', views.lab_manager_dashboard, name='lab_manager_dashboard'),
]