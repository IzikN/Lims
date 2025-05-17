from django.urls import path
from . import views

urlpatterns = [
    path('customer-service/', views.customer_service_dashboard, name='customer_service_dashboard'),
    path('test-request/', views.test_request_form_view, name='test_request_form'),
    path('intake-dashboard/', views.intake_dashboard, name='intake_dashboard'),
    path('test-request/<int:pk>/', views.test_request_detail, name='test_request_detail'),
]
