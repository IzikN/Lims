from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Sample

@login_required
def submit_sample(request):
    if request.user.role != 'client':
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST['name']
        sample_type = request.POST['sample_type']
        description = request.POST['description']
        is_urgent = bool(request.POST.get('is_urgent'))

        Sample.objects.create(
            client=request.user,
            name=name,
            sample_type=sample_type,
            description=description,
            date_received=None,
            is_urgent=is_urgent,
        )
        return render(request, 'samples/submission_success.html')

    return render(request, 'samples/submit_sample.html')
