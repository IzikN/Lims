from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
     path('register/', views.choose_role, name='register'),
    path('register/client/', views.register_client, name='register_client'),
    path('register/staff/', views.register_staff, name='register_staff'),
    path('choose-role/', views.choose_role, name='choose_role'),

    path('dashboard/client/', views.client_dashboard, name='client_dashboard'),
    path('dashboard/analyst/', views.analyst_dashboard, name='analyst_dashboard'),
    path('dashboard/lab-manager/', views.lab_manager_dashboard, name='lab_manager_dashboard'),
    path('sample/submit/', views.submit_sample_form, name='submit_sample_form'),
    path('logout/', views.logout_view, name='logout'),
]

    
