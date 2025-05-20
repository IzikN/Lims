from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Client, TestRequest, Sample
from django.utils import timezone
from .forms import TestAssignmentForm
from .forms import SubmitResultForm 
from .models import TestAssignment, AnalystProfile

@login_required
def start_test(request, pk):
    assignment = get_object_or_404(TestAssignment, pk=pk, analyst=request.user)

    if assignment.status != 'assigned':
        messages.warning(request, "This test cannot be started.")
        return redirect('analyst_dashboard')

    assignment.status = 'in_progress'
    assignment.save()
    messages.success(request, f"Started test for Sample {assignment.sample.sample_id}.")
    return redirect('analyst_dashboard')


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
    client_id = request.GET.get('client_id')
    form = None
    samples = None

    if client_id:
        # Get Client object by client_id string field
        client = get_object_or_404(Client, client_id=client_id)
        samples = Sample.objects.filter(client=client)

        if request.method == 'POST':
            form = TestAssignmentForm(request.POST, client_id=client_id)
            if form.is_valid():
                form.save()
                # Redirect back with same client_id to continue assignments
                return redirect(f"{request.path}?client_id={client_id}")
        else:
            form = TestAssignmentForm(client_id=client_id)
    else:
        form = None

    return render(request, 'samples/assign_test.html', {
        'form': form,
        'client_id': client_id,
        'samples': samples,
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



def intake_dashboard(request):
    test_requests = TestRequest.objects.all()

    # Get filter values from query parameters
    client_name = request.GET.get('client_name')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter by client name
    if client_name:
        test_requests = test_requests.filter(client__name__icontains=client_name)

    # Filter by status
    if status:
        test_requests = test_requests.filter(status__iexact=status)

    # Filter by date range
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            test_requests = test_requests.filter(created_at__gte=start)
        except ValueError:
            pass  # Ignore invalid date

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            test_requests = test_requests.filter(created_at__lte=end)
        except ValueError:
            pass

    # Order by latest first
    test_requests = test_requests.order_by('-created_at')

    context = {
        'test_requests': test_requests,
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
    # Check if user is in 'Analyst' group
    if not request.user.groups.filter(name='Analyst').exists():
        return redirect('unauthorized')  # You can create a simple page

    analyst_profile = AnalystProfile.objects.get(user=request.user)
    assignments = TestAssignment.objects.filter(analyst=analyst_profile)

    return render(request, 'samples/analyst_dashboard.html', {
        'assignments': assignments
    })
