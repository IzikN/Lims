from django.urls import path
from . import views
from django.urls import path
from .views import SampleCreateView
from django.views.generic import TemplateView

urlpatterns = [
    path('samples/submit/', SampleCreateView.as_view(), name='sample_submit'),
    path('samples/success/', TemplateView.as_view(template_name='samples/success.html'), name='sample_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('submit/', views.submit_sample, name='submit_sample'),
    path('intake/', views.intake_dashboard, name='intake_dashboard'),
    path('assign/<int:sample_id>/', views.assign_test, name='assign_test'),
    path('analyst/', views.analyst_dashboard, name='analyst_dashboard'),
    path('submit-result/<int:assignment_id>/', views.submit_result, name='submit_result'),
    path('start-test/<int:assignment_id>/', views.start_test, name='start_test'),
    path('labmanager/review/', views.review_submissions, name='review_submissions'),
    path('labmanager/review/<int:assignment_id>/', views.review_result, name='review_result'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),


]
