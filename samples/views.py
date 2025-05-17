from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render
from .models import TestRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TestRequest, Client
from .models import Sample
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Client, TestRequest, Sample
from django.utils import timezone

def generate_unique_client_id():
    prefix = "JGLSP"  # or your desired prefix
    number = 2500     # starting number

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

