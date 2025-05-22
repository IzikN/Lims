from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client, TestRequest, Sample
from django.utils import timezone
from .forms import TestAssignmentForm
from .forms import SubmitResultForm 
from .models import TestAssignment, AnalystProfile
from datetime import datetime
from collections import defaultdict
from django.db.models import Count, Sum
from django.utils import timezone
from .models import TestAssignment, TestRequest
from django.views.decorators.http import require_http_methods
from .models import ReviewLog

def sync_test_request_status(client):
    test_request = TestRequest.objects.filter(client=client).first()
    if not test_request:
        return

    assignments = TestAssignment.objects.filter(samples__client=client).distinct()

    if all(a.status == 'completed' for a in assignments):
        test_request.status = 'completed'
    elif all(a.status == 'cancelled' for a in assignments):
        test_request.status = 'cancelled'
    elif any(a.status == 'in_progress' for a in assignments):
        test_request.status = 'in_progress'
    else:
        test_request.status = 'assigned'

    test_request.save()


@login_required
@require_http_methods(["GET", "POST"])
def enter_result(request, assignment_id):
    assignment = get_object_or_404(TestAssignment, id=assignment_id)

    if request.method == 'POST':
        result = request.POST.get('result')
        if not result:
            messages.error(request, "Result cannot be empty.")
            return redirect('enter_result', assignment_id=assignment_id)

        assignment.result = result
        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.save()

        sync_test_request_status(assignment.samples.first().client)
        messages.success(request, "Result submitted successfully.")
        return redirect('analyst_dashboard')

    return render(request, 'samples/enter_result.html', {'assignment': assignment})

@login_required
def start_test(request, assignment_id):
    assignment = get_object_or_404(TestAssignment, id=assignment_id)

    if not assignment.started:
        assignment.started = True
        assignment.started_at = timezone.now()
        assignment.status = 'in_progress'
        assignment.save()
        messages.success(request, "Test started successfully.")
    else:
        messages.info(request, "Test already started.")

    return redirect('analyst_dashboard')


@login_required
def review_test(request, assignment_id):
    assignment = get_object_or_404(TestAssignment, pk=assignment_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        reviewer = request.user

        # Save current review
        ReviewLog.objects.create(
            assignment=assignment,
            reviewer=reviewer,
            comments=comments,
            decision='approved' if action == 'approve' else 'rejected'
        )

        assignment.review_comments = comments
        assignment.reviewer = reviewer
        assignment.latest_review = timezone.now()

        if action == 'approve':
            assignment.review_status = 'approved'
            assignment.status = 'completed'
        elif action == 'reject':
            assignment.review_status = 'rejected'
            assignment.status = 'in_progress'

        assignment.save()
        return redirect('result_overview')

    return render(request, 'samples/review_test.html', {'assignment': assignment})

@login_required
def result_overview(request):

    results_by_client = defaultdict(list)

    assignments = TestAssignment.objects.select_related('analyst__user').prefetch_related('samples')

    for assignment in assignments:
        # Assuming all samples in this assignment belong to the same client
        client_id = assignment.samples.first().client_id if assignment.samples.exists() else 'Unknown'

        for sample in assignment.samples.all():
            results_by_client[client_id].append({
                'sample_id': sample.sample_id,
                'test': assignment.test_parameter,
                'sub_test': assignment.sub_parameter,
                'result': assignment.result,
                'analyst': assignment.analyst.user.get_full_name() if assignment.analyst else 'Unknown',
                'assignment_id': assignment.id 
            })

    return render(request, 'samples/result_overview.html', {
        'results_by_client': dict(results_by_client)
    })

@login_required
def submit_test_result(request, pk):
    assignment = get_object_or_404(TestAssignment, pk=pk, analyst=request.user)

    if request.method == 'POST':
        form = SubmitResultForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.status = 'submitted'
            assignment.save()
            messages.success(request, f"Result for {assignment.sample.sample_id} submitted.")
            return redirect('analyst_dashboard')
    else:
        form = SubmitResultForm(instance=assignment)

    return render(request, 'samples/submit_result.html', {'form': form, 'assignment': assignment})

@login_required
def assign_test_view(request):
    if not request.user.role == 'lab_manager':
        return redirect('no_permission')

    client_id = request.GET.get('client_id')
    if not client_id:
        messages.error(request, "No client ID provided.")
        return redirect('intake_dashboard')

    client = get_object_or_404(Client, client_id=client_id)
    samples = Sample.objects.filter(client=client)

    if request.method == 'POST':
        sample_ids = request.POST.getlist('samples')
        test_params = request.POST.getlist('test_parameter[]')
        sub_params = request.POST.getlist('sub_parameter[]')
        analysts = request.POST.getlist('analyst[]')
        deadlines = request.POST.getlist('deadline[]')

        print("Sample IDs:", sample_ids)
        print("Test Parameters:", test_params)
        print("Sub Parameters:", sub_params)
        print("Analysts:", analysts)
        print("Deadlines:", deadlines)

        sample_qs = Sample.objects.filter(id__in=sample_ids)

        for i in range(len(test_params)):
            analyst = get_object_or_404(AnalystProfile, id=analysts[i])
            test_param = test_params[i]
            sub_param = sub_params[i] if test_param == 'proximate' else None
            deadline = deadlines[i]

            assignment = TestAssignment.objects.create(
                analyst=analyst,
                test_parameter=test_param,
                sub_parameter=sub_param,
                deadline=deadline,
                status='assigned'
            )
            assignment.samples.set(sample_qs)

        messages.success(request, "Tests assigned successfully!")
        return redirect('intake_dashboard')

    analysts = AnalystProfile.objects.all()
    return render(request, 'samples/assign_test.html', {
        'client_id': client_id,
        'samples': samples,
        'analysts': analysts,
        'client': client,
    })

def generate_unique_client_id():
    prefix = "JGLSP"  
    number = 2500     

    while True:
        client_id = f"{prefix}{number}"
        if not Client.objects.filter(client_id=client_id).exists():
            return client_id
        number += 1

@login_required
def test_request_form_view(request):
    if request.method == 'POST':
        client_name = request.POST['client_name']
        phone = request.POST['phone']
        client_id = generate_unique_client_id()

        # Get or create the client using client_id
        client, created = Client.objects.get_or_create(
            client_id=client_id,
            defaults={
                'name': client_name,
                'phone': phone,
                'email': request.POST.get('email'),
                'organization': request.POST.get('organization'),
                'address': request.POST.get('address'),
            }
        )

        # Create the test request
        test_request = TestRequest.objects.create(
            client=client,
            organization=request.POST.get('organization'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            number_of_samples=request.POST.get('number_of_samples'),
            nature_of_samples=request.POST.get('nature_of_samples', ''),
            proposed_date_of_collection=request.POST.get('proposed_date_of_collection'),
            total_amount_charged=request.POST.get('total_amount'),
            amount_paid=request.POST.get('amount_paid'),
            name_of_receiver=request.POST.get('receiver'),
            job_description=request.POST.get('job_description'),
            signature=request.POST.get('signature'),
            submitted_by=request.user,
            created_at=timezone.now(),
        )

        # Handle multiple samples
        sample_ids = request.POST.getlist('sample_ids[]')
        weights = request.POST.getlist('sample_weights[]')

        for i in range(len(sample_ids)):
            params = request.POST.getlist(f'sample_parameters_{i}[]')
            Sample.objects.create(
                client=client,
                test_request=test_request,
                sample_id=sample_ids[i],
                weight=weights[i],
                nature=request.POST.get('nature_of_samples'),
                parameters=", ".join(params)
            )

        messages.success(request, "Test request submitted successfully.")
        return redirect('intake_dashboard')

    # For GET request
    client_id = generate_unique_client_id()
    return render(request, 'samples/test_request_form.html', {
        'client_id': client_id
    })


def is_customer_service(user):
    return user.groups.filter(name='Customer Service').exists()

@login_required
def customer_service_dashboard(request):
    return render(request, 'samples/customer_service_dashboard.html')

def is_customer_service(user):
    return user.groups.filter(name='Customer Service').exists()


def is_lab_manager_or_customer_service(user):
    return user.groups.filter(name__in=['Lab Manager', 'Customer Service']).exists()


@login_required
def intake_dashboard(request):
    test_requests = TestRequest.objects.all()

    # Filters
    client_name = request.GET.get('client_name')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if client_name:
        test_requests = test_requests.filter(client__name__icontains=client_name)

    if status:
        test_requests = test_requests.filter(status__iexact=status)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            test_requests = test_requests.filter(created_at__gte=start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            test_requests = test_requests.filter(created_at__lte=end)
        except ValueError:
            pass

    test_requests = test_requests.order_by('-created_at')

    # Summary stats
    total_clients = test_requests.values('client').distinct().count()
    total_samples = test_requests.aggregate(total=Sum('number_of_samples'))['total'] or 0

    assigned_count = test_requests.filter(status='assigned').count()
    pending_count = test_requests.filter(status='pending').count()
    in_progress_count = test_requests.filter(status='in_progress').count()
    completed_count = test_requests.filter(status='completed').count()
    cancelled_count = test_requests.filter(status='cancelled').count()

    context = {
        'test_requests': test_requests,
        'total_clients': total_clients,
        'total_samples': total_samples,
        'assigned_count': assigned_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'filters': {
            'client_name': client_name or '',
            'status': status or '',
            'start_date': start_date or '',
            'end_date': end_date or '',
        }
    }

    return render(request, 'samples/intake_dashboard.html', context)


@login_required
def test_request_detail(request, pk):
    test_request = get_object_or_404(TestRequest, pk=pk)
    return render(request, 'samples/test_request_detail.html', {'test_request': test_request})



@login_required
def analyst_dashboard(request):
    analyst = request.user.analystprofile
    test_type_filter = request.GET.get('test_type', '')

    assignments = TestAssignment.objects.filter(analyst=analyst).prefetch_related('samples')

    if test_type_filter:
        assignments = assignments.filter(test_parameter=test_type_filter)

    today = timezone.localdate()

    grouped_assignments = [
        {
            'label': 'Overdue Tests',
            'items': [a for a in assignments if a.deadline and a.deadline < today and a.status in ['assigned', 'in_progress']]
        },
        {
            'label': 'Due Today',
            'items': [a for a in assignments if a.deadline == today and a.status in ['assigned', 'in_progress']]
        },
        {
            'label': 'Upcoming Tests',
            'items': [a for a in assignments if a.deadline and a.deadline > today and a.status in ['assigned', 'in_progress']]
        },
        {
            'label': 'Completed',
            'items': [a for a in assignments if a.status == 'completed']
        },
    ]

    has_critical_deadlines = any(group['items'] for group in grouped_assignments[:2])  # Overdue or Due Today

    test_types = TestAssignment.objects.values_list('test_parameter', flat=True).distinct()

    return render(request, 'samples/analyst_dashboard.html', {
        'grouped_assignments': grouped_assignments,
        'today': today,
        'has_critical_deadlines': has_critical_deadlines,
        'test_types': test_types,
        'selected_test_type': test_type_filter,
    })
