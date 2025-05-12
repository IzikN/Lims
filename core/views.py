from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from inventory.models import Reagent, Equipment
#from sample.models import Sample, AnalysisAssignment
from django.utils import timezone

def home(request):
    return render(request, 'core/home.html')


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
        'Proximate': samples.filter(test_type='Proximate').count(),
        'Aflatoxin': samples.filter(test_type='Aflatoxin').count(),
        'Gross Energy': samples.filter(test_type='Gross Energy').count(),
        'Vitamins': samples.filter(test_type='Vitamins').count(),
        'Water': samples.filter(test_type='Water').count(),
        'Microbial': samples.filter(test_type='Microbial').count(),
    }

    expiring_reagents = Reagent.objects.filter(expiry_date__lte=timezone.now().date() + timezone.timedelta(days=7))
    calibration_due = Equipment.objects.filter(next_calibration_due__lte=timezone.now().date() + timezone.timedelta(days=7))
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
