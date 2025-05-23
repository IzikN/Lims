from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from inventory.models import Reagent, Equipment
from samples.models import Sample, TestAssignment
from django.utils import timezone
from samples.models import TestRequest
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from samples.models import Sample
from inventory.models import Equipment
from inventory.models import Reagent
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import datetime


def home(request):
    return render(request, 'core/home.html')


def result_overview(request):
    # Count test requests by status
    assigned = TestRequest.objects.filter(status='assigned').count()
    in_progress = TestRequest.objects.filter(status='in_progress').count()
    submitted = TestRequest.objects.filter(status='submitted').count()
    completed = TestRequest.objects.filter(status='completed').count()

    context = {
        'assigned': assigned,
        'in_progress': in_progress,
        'submitted': submitted,
        'completed': completed,
    }

    return render(request, 'samples/results_overview.html', context)


@login_required
def lab_manager_dashboard(request):
    if request.user.role != 'lab_manager':
        return redirect('home')

    # Fetch all samples
    samples = Sample.objects.all()
    total_samples = samples.count()
    pending = samples.filter(status='Pending').count()
    in_progress = samples.filter(status='In Progress').count()
    completed = samples.filter(status='Completed').count()

    # Count samples per test type
    test_types = {
        label: samples.filter(test_type=code).count()
        for code, label in Sample.TEST_TYPE_CHOICES
    }

    # Track expiring reagents and calibration due equipment
    expiring_reagents = Reagent.objects.filter(expiry_date__lte=timezone.now())
    calibration_due = Equipment.objects.filter(next_calibration_due__lte=timezone.now())

    # Fetch all test assignments
    assignments = TestAssignment.objects.all()

    # Fetch completed and approved assignments for COA generation
    completed_assignments = TestAssignment.objects.filter(
        review_status='approved',
        status='completed'
    )

    context = {
        'total_samples': total_samples,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'test_types': test_types,
        'expiring_reagents': expiring_reagents,
        'calibration_due': calibration_due,
        'assignments': assignments,
        'completed_assignments': completed_assignments,
    }

    return render(request, 'core/lab_manager_dashboard.html', context)


@require_GET
@login_required
def filter_dashboard_data(request):
    test_type = request.GET.get('test_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    invoices = Invoice.objects.all()

    if test_type:
        invoices = invoices.filter(test_request__sample__test_type=test_type)

    if start_date:
        invoices = invoices.filter(date_generated__gte=start_date)
    if end_date:
        invoices = invoices.filter(date_generated__lte=end_date)

    total_filtered = invoices.aggregate(total=Sum('total_amount'))['total'] or 0

    return JsonResponse({'total_filtered': float(total_filtered)})
