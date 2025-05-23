from django.urls import path
from . import views
from .views import certificate_of_analysis

urlpatterns = [
    path('generate-coa/<str:client_id>/', views.generate_coa_view, name='generate_coa'),
    path('coa/<str:client_id>/', certificate_of_analysis, name='certificate_of_analysis'),
    path('invoice/<int:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
    path('analyst/start-test/<int:assignment_id>/', views.start_test, name='start_test'),
    path('manager/results/', views.result_overview, name='result_overview'),
    path('analyst/enter-result/<int:assignment_id>/', views.enter_result, name='enter_result'),
    path('analyst/dashboard/', views.analyst_dashboard, name='analyst_dashboard'),
    path('samples/assign-test/', views.assign_test_view, name='assign_test'),
    path('assignments/<int:assignment_id>/start/', views.start_test, name='start_test'),
    path('assignments/<int:assignment_id>/submit/', views.submit_test_result, name='submit_result'),
    path('customer-service/', views.customer_service_dashboard, name='customer_service_dashboard'),
    path('test-request/', views.test_request_form_view, name='test_request_form'),
    path('intake-dashboard/', views.intake_dashboard, name='intake_dashboard'),
    path('test-request/<int:pk>/', views.test_request_detail, name='test_request_detail'),
    path('samples/assignments/<int:assignment_id>/review/', views.review_test, name='review_test'),
]
