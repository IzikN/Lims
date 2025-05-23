from django.urls import path
from . import views

urlpatterns = [
    path('equipment-log/create/', views.equipment_log_create, name='equipment_log_create'),
    path('equipment-log/list/', views.equipment_log_list, name='equipment_log_list'),
    path('equipment-log/pdf/<int:pk>/', views.equipment_log_pdf, name='equipment_log_pdf'),
    path('reagents/export/pdf/', views.export_reagent_pdf, name='export_reagent_pdf'),
    path('equipment/export/pdf/', views.export_equipment_pdf, name='export_equipment_pdf'),
    path('equipment/export/csv/', views.export_equipment_csv, name='export_equipment_csv'),
    path('reagents/export/csv/', views.export_reagent_csv, name='export_reagent_csv'),
    path('reagents/', views.reagent_list, name='reagent_list'),
    path('reagents/add/', views.add_reagent, name='add_reagent'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.add_equipment, name='add_equipment'),
]
