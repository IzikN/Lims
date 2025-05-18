from django.urls import path
from . import views


urlpatterns = [
    path('analyst/dashboard/', views.analyst_dashboard, name='analyst_dashboard'),
    path('assign-tests/', views.assign_test_view, name='assign_tests'),
    path('assignments/<int:assignment_id>/start/', views.start_test, name='start_test'),
    path('assignments/<int:assignment_id>/submit/', views.submit_test_result, name='submit_result'),
    path('customer-service/', views.customer_service_dashboard, name='customer_service_dashboard'),
    path('test-request/', views.test_request_form_view, name='test_request_form'),
    path('intake-dashboard/', views.intake_dashboard, name='intake_dashboard'),
    path('test-request/<int:pk>/', views.test_request_detail, name='test_request_detail'),

]
