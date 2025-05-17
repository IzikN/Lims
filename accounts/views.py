from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import ClientRegistrationForm, StaffRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib import messages

def register(request):
    return render(request, 'accounts/register.html')

def choose_role(request):
    return render(request, 'accounts/choose_role.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # Redirect based on role
            if user.role == 'client':
                return redirect('client_dashboard')
            elif user.role == 'analyst':
                return redirect('analyst_dashboard')
            elif user.role == 'lab_manager':
                return redirect('lab_manager_dashboard')
            elif user.role == 'customer_service':
                return redirect('customer_service_dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'accounts/login.html')


def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = ClientRegistrationForm()
    return render(request, 'accounts/register_client.html', {'form': form})


def register_staff(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff registered successfully.')
            return redirect('login')
    else:
        form = StaffRegistrationForm()
    return render(request, 'accounts/register_staff.html', {'form': form})


@login_required
def client_dashboard(request):
    return render(request, 'samples/client_dashboard.html')

@login_required
def analyst_dashboard(request):
    return render(request, 'samples/analyst_dashboard.html')

@login_required
def lab_manager_dashboard(request):
    return render(request, 'core/lab_manager_dashboard.html')

@login_required
def submit_sample_form(request):
    return render(request, 'samples/test_request_form.html')



def logout_view(request):
    logout(request)
    return redirect('login')
