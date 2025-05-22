from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from inventory.models import Reagent, Equipment
#from sample.models import Sample, AnalysisAssignment
from django.utils import timezone
from samples.models import TestRequest

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

    samples = Sample.objects.all()
    total_samples = samples.count()
    pending = samples.filter(status='Pending').count()
    in_progress = samples.filter(status='In Progress').count()
    completed = samples.filter(status='Completed').count()

    test_types = {
        'Proximate': samples.filter(test_type='PROX').count(),
        'Aflatoxin': samples.filter(test_type='AFLX').count(),
        'Gross Energy': samples.filter(test_type='GREN').count(),
        'Vitamins': samples.filter(test_type='VIT').count(),
        'Water': samples.filter(test_type='WAT').count(),
        'Microbial': samples.filter(test_type='MIC').count(),
    }

    expiring_reagents = Reagent.objects.filter(expiry_date__lte=timezone.now())
    calibration_due = Equipment.objects.filter(next_calibration_due__lte=timezone.now())
    assignments = AnalysisAssignment.objects.all()

    context = {
        'total_samples': total_samples,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'test_types': test_types,
        'expiring_reagents': expiring_reagents,
        'calibration_due': calibration_due,
        'assignments': assignments,
    }

    return render(request, 'core/lab_manager_dashboard.html', context)
