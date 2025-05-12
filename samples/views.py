from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Sample
from django.utils import timezone
from .models import TestAssignment
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import SampleForm
from django.contrib import messages
from .models import Sample, TestRequest, Attachment
from django.utils.crypto import get_random_string


@login_required
def dashboard(request):
    if request.user.role == 'lab_manager':
        return redirect('intake_dashboard')
    elif request.user.role == 'analyst':
        return redirect('analyst_dashboard')
    elif request.user.role == 'client':
        return redirect('client_dashboard')
    else:
        return redirect('home')  # or raise an error


@login_required
def intake_dashboard(request):
    if request.user.role != 'lab_manager':
        return redirect('lab-dashboard')

    pending_samples = Sample.objects.filter(status='pending')

    if request.method == 'POST':
        sample_id = request.POST.get('sample_id')
        if sample_id:
            try:
                sample = Sample.objects.get(id=sample_id)
                sample.status = 'received'
                sample.date_received = timezone.now()
                sample.save()
            except Sample.DoesNotExist:
                pass  # or handle error message

    return render(request, 'samples/intake_dashboard.html', {'samples': pending_samples})



class SampleCreateView(CreateView):
    model = Sample
    form_class = SampleForm
    template_name = 'samples/sample_form.html'
    success_url = reverse_lazy('sample_success')


@login_required
def submit_sample(request):
    if request.method == 'POST':
        sample_id = request.POST.get('sample_id')
        name = request.POST.get('name')
        sample_type = request.POST.get('sample_type')
        client_company = request.POST.get('client_company')  # ✅ Fixed line
        description = request.POST.get('description')
        client_email = request.POST.get('client_email')
        client_company_address = request.POST.get('client_company_address')
        weight = request.POST.get('weight')
        analysis_type = request.POST.get('analysis_type')
        is_urgent = 'is_urgent' in request.POST
        attachment = request.FILES.get('attachment')

        try:
            # Create Sample
            sample = Sample.objects.create(
                sample_id=sample_id,
                name=name,
                sample_type=sample_type,
                client_company=client_company,  # ✅ Include in model
                description=description,
                client_email=client_email,
                client_company_address=client_company_address,
                weight=weight,
                is_urgent=is_urgent,
                received_by=request.user  # Assumes user is logged in
            )

            # Create Test Request
            TestRequest.objects.create(
                sample=sample,
                test_type=analysis_type,
                tests_required=analysis_type,
                created_by=request.user
            )

            # Save Attachment
            if attachment:
                Attachment.objects.create(
                    sample=sample,
                    file=attachment,
                    label='Initial Upload'
                )

            messages.success(request, f"Sample {sample_id} submitted successfully.")
            return redirect('sample_list')

        except Exception as e:
            messages.error(request, f"Error submitting sample: {str(e)}")

    return render(request, 'samples/submit_sample.html')



@login_required
def assign_test(request, sample_id):
    if request.user.role != 'lab_manager':
        return redirect('dashboard')

    sample = Sample.objects.get(id=sample_id)
    analysts = User.objects.filter(role='analyst')

    if request.method == 'POST':
        test_type = request.POST['test_type']
        analyst_id = request.POST['analyst']
        analyst = User.objects.get(id=analyst_id)

        TestAssignment.objects.create(
            sample=sample,
            analyst=analyst,
            test_type=test_type,
            assigned_by=request.user,
        )

        sample.status = 'in_progress'
        sample.save()
        return redirect('intake_dashboard')

    return render(request, 'samples/assign_test.html', {
        'sample': sample,
        'analysts': analysts,
    })

@login_required
def analyst_dashboard(request):
    if request.user.role != 'analyst':
        return redirect('dashboard')

    assignments = TestAssignment.objects.filter(analyst=request.user).order_by('-assigned_at')
    return render(request, 'samples/analyst_dashboard.html', {'assignments': assignments})

@login_required
def submit_result(request, assignment_id):
    assignment = get_object_or_404(TestAssignment, id=assignment_id, analyst=request.user)

    if request.method == 'POST':
        assignment.result_data = request.POST['result_data']
        if 'result_file' in request.FILES:
            assignment.result_file = request.FILES['result_file']

        assignment.status = 'submitted'
        assignment.completed_at = timezone.now()
        assignment.save()

        return redirect('analyst_dashboard')

    return render(request, 'samples/submit_result.html', {'assignment': assignment})

@login_required
def start_test(request, assignment_id):
    assignment = get_object_or_404(TestAssignment, id=assignment_id, analyst=request.user)
    assignment.status = 'in_progress'
    assignment.started_at = timezone.now()
    assignment.save()
    return redirect('analyst_dashboard')

@login_required
def review_submissions(request):
    if request.user.role != 'lab_manager':
        return redirect('dashboard')

    submissions = TestAssignment.objects.filter(status='submitted').order_by('-completed_at')
    return render(request, 'samples/review_submissions.html', {'submissions': submissions})
@login_required
def review_result(request, assignment_id):
    if request.user.role != 'lab_manager':
        return redirect('dashboard')

    assignment = get_object_or_404(TestAssignment, id=assignment_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments')

        if action == 'approve':
            assignment.review_status = 'approved'
            assignment.status = 'completed'
        else:
            assignment.review_status = 'rejected'
            assignment.status = 'in_progress'

        assignment.review_comments = comments
        assignment.reviewed_by = request.user
        assignment.reviewed_at = timezone.now()
        assignment.save()
        return redirect('review_submissions')

    return render(request, 'samples/review_result.html', {'assignment': assignment})

@login_required
def client_dashboard(request):
    if request.user.role != 'client':
        return redirect('dashboard')

    samples = Sample.objects.filter(client=request.user).order_by('-date_submitted')
    assignments = TestAssignment.objects.filter(sample__in=samples)

    assignments_by_sample = {}
    for assign in assignments:
        assignments_by_sample.setdefault(assign.sample.id, []).append(assign)

    return render(request, 'samples/client_dashboard.html', {
        'samples': samples,
        'assignments_by_sample': assignments_by_sample,
    })
@login_required
def submit_sample(request):
    if request.user.role != 'customer_service':
        return redirect('home')

    if request.method == 'POST':
        sample_id = request.POST['sample_id']
        client_company = request.POST['client_company']
        client_name = request.POST['client_name']
        name = request.POST['name']
        sample_type = request.POST['sample_type']
        description = request.POST['description']
        weight = request.POST['weight']
        is_urgent = bool(request.POST.get('is_urgent'))

        Sample.objects.create(
            sample_id=sample_id,
            name=name,
            sample_type=sample_type,
            description=description,
            client_name=client_name,
            client_company=client_company,
            weight=weight,
            date_received=timezone.now(),
            is_urgent=is_urgent,
            status='received',
        )
        return render(request, 'samples/submission_success.html')

    return render(request, 'samples/submit_sample.html')
