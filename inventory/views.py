from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Reagent, Equipment
from .forms import ReagentForm, EquipmentForm

def is_lab_manager(user):
    return user.is_authenticated and user.role == 'lab_manager'

@login_required
def reagent_list(request):
    reagents = Reagent.objects.all().order_by('-date_received')
    return render(request, 'inventory/reagent_list.html', {'reagents': reagents})

@login_required
def add_reagent(request):
    if request.user.role != 'lab_manager':
        messages.warning(request, "Access denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ReagentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Reagent added successfully!")
            return redirect('reagent_list')
        else:
            messages.error(request, "There was an error with the form.")
    else:
        form = ReagentForm()

    return render(request, 'inventory/reagent_form.html', {'form': form})


@login_required
def equipment_list(request):
    equipment = Equipment.objects.all().order_by('-last_calibration_date')
    return render(request, 'inventory/equipment_list.html', {'equipment': equipment})

@login_required
def add_equipment(request):
    if not is_lab_manager(request.user):
        return redirect('equipment_list')

    form = EquipmentForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.added_by = request.user
        instance.save()
        return redirect('equipment_list')
    return render(request, 'inventory/equipment_form.html', {'form': form})
