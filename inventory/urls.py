from django.urls import path
from . import views

urlpatterns = [
    path('reagents/', views.reagent_list, name='reagent_list'),
    path('reagents/add/', views.add_reagent, name='add_reagent'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.add_equipment, name='add_equipment'),
]
