from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Reagent, Equipment
from .forms import ReagentForm, EquipmentForm
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .forms import ReagentFilterForm
from .forms import EquipmentFilterForm
import csv
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import EquipmentLog
from .forms import EquipmentLogForm
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit

def equipment_log_create(request):
    if request.method == 'POST':
        form = EquipmentLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('equipment_log_list')
    else:
        form = EquipmentLogForm()
    return render(request, 'inventory/equipment_log_form.html', {'form': form})

def equipment_log_list(request):
    logs = EquipmentLog.objects.order_by('-start_time')
    paginator = Paginator(logs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory/equipment_log_list.html', {'page_obj': page_obj})

def equipment_log_pdf(request, pk):
    log = get_object_or_404(EquipmentLog, pk=pk)
    html = render_to_string('equipment_log_pdf.html', {'log': log})
    
#     Configure pdfkit (you may need to adjust the path to wkhtmltopdf)
    options = {
        'page-size': 'A4',
        'encoding': "UTF-8",
    }
    pdf = pdfkit.from_string(html, False, options=options)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="equipment_log_{log.pk}.pdf"'
    return response


def export_reagent_pdf(request):
    reagents = Reagent.objects.all()
    template_path = 'inventory/reagent_pdf.html'
    context = {'reagents': reagents}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reagent_list.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response



def export_equipment_pdf(request):
    equipments = Equipment.objects.all()
    template_path = 'inventory/equipment_pdf.html'
    context = {'equipments': equipments}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="equipment_list.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response


def export_equipment_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipment_list.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Model', 'Serial Number', 'Status', 'Added By', 'Date Added'])

    for eq in Equipment.objects.all():
        writer.writerow([eq.name, eq.model_number, eq.serial_number, eq.status, eq.added_by, eq.date_added])

    return response


def export_reagent_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reagent_list.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Quantity', 'Unit', 'Location', 'Date Added'])

    for reagent in Reagent.objects.all():
        writer.writerow([reagent.name, reagent.quantity, reagent.unit, reagent.location, reagent.date_added])

    return response


@login_required
def equipment_list(request):
    query = request.GET.get('q')
    if query:
        equipments = Equipment.objects.filter(name__icontains=query)
    else:
        equipments = Equipment.objects.all()

    # Handle downloads first
    if 'download_csv' in request.GET:
        return download_csv(equipments, 'equipment')
    if 'download_pdf' in request.GET:
        return download_pdf(equipments, 'equipment')

    return render(request, 'inventory/equipment_list.html', {
        'equipments': equipments
    })


@login_required
def reagent_list(request):
    reagents = Reagent.objects.all()
    filter_form = ReagentFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('name'):
            reagents = reagents.filter(name__icontains=filter_form.cleaned_data['name'])
        if filter_form.cleaned_data.get('supplier'):
            reagents = reagents.filter(supplier__icontains=filter_form.cleaned_data['supplier'])

    if 'download_csv' in request.GET:
        return download_csv(reagents, 'reagent')
    if 'download_pdf' in request.GET:
        return download_pdf(reagents, 'reagent')

    return render(request, 'inventory/reagent_list.html', {
        'reagents': reagents,
        'filter_form': filter_form,
    })


def download_csv(queryset, model_type):
    from django.http import HttpResponse
    import csv

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_type}_list.csv"'
    writer = csv.writer(response)

    if model_type == 'equipment':
        writer.writerow(['Name', 'Category', 'Date Added'])
        for item in queryset:
            writer.writerow([item.name, item.category, item.date_added])
    elif model_type == 'reagent':
        writer.writerow(['Name', 'Supplier', 'Date Acquired'])
        for item in queryset:
            writer.writerow([item.name, item.supplier, item.date_acquired])

    return response


def download_pdf(queryset, model_type):
    from django.http import HttpResponse

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{model_type}_list.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    title = f"{model_type.capitalize()} List"
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, title)
    y -= 30

    p.setFont("Helvetica", 12)
    if model_type == 'equipment':
        p.drawString(50, y, "Name | Category | Date Added")
        y -= 20
        for item in queryset:
            p.drawString(50, y, f"{item.name} | {item.category} | {item.date_added}")
            y -= 20
            if y < 50:
                p.showPage()
                y = height - 50
    elif model_type == 'reagent':
        p.drawString(50, y, "Name | Supplier | Date Acquired")
        y -= 20
        for item in queryset:
            p.drawString(50, y, f"{item.name} | {item.supplier} | {item.date_acquired}")
            y -= 20
            if y < 50:
                p.showPage()
                y = height - 50

    p.showPage()
    p.save()
    return response


def is_lab_manager(user):
    return user.is_authenticated and user.role == 'lab_manager'



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

    # Pass the model name to the template explicitly
    model_name = form._meta.model.__name__

    return render(request, 'inventory/reagent_form.html', {
        'form': form,
        'model_name': model_name,
    })


@login_required
def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save(commit=False)
            equipment.added_by = request.user
            equipment.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'inventory/equipment_form.html', {'form': form, 'model_name': 'equipment'})

@login_required
def add_reagent(request):
    if request.method == 'POST':
        form = ReagentForm(request.POST, request.FILES)
        if form.is_valid():
            reagent = form.save(commit=False)
            reagent.added_by = request.user
            reagent.save()
            return redirect('reagent_list')
    else:
        form = ReagentForm()
    return render(request, 'inventory/reagent_form.html', {'form': form, 'model_name': 'reagent'})
