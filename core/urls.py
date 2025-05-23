from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.lab_manager_dashboard, name='lab_manager_dashboard'),
    path('dashboard/filter-data/', views.filter_dashboard_data, name='filter_dashboard_data'),
    path('result-overview/', views.result_overview, name='result_overview'),
    path('lab-manager/dashboard/', views.lab_manager_dashboard, name='lab_manager_dashboard'),
]
