from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer, Street

# Create your views here.

@login_required(login_url='login')
def customer_list(request):
    if request.user.role not in ['manager', 'staff']:
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_street':
            region = request.POST.get('region')
            district = request.POST.get('district')
            street_name = request.POST.get('street_name')
            
            if region and district and street_name:
                Street.objects.get_or_create(
                    region=region,
                    district=district,
                    street_name=street_name
                )
                messages.success(request, f'Street "{street_name}" added successfully.')
            else:
                messages.error(request, 'Please fill in all street fields.')
            return redirect('customer_list')
        
        else:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number')
            street_id = request.POST.get('street')
            has_mita = request.POST.get('has_mita', 'no')
            total_units = request.POST.get('total_units', '0')
            
            if first_name and phone_number and street_id:
                street = Street.objects.get(id=street_id)
                
                # Parse total_units - default to 0 if not provided or invalid
                try:
                    units_value = float(total_units) if has_mita == 'yes' and total_units else 0
                except (ValueError, TypeError):
                    units_value = 0
                
                Customer.objects.create(
                    first_name=first_name,
                    last_name=last_name or '',
                    phone_number=phone_number,
                    street=street,
                    total_units=units_value
                )
                messages.success(request, f'Customer "{first_name} {last_name}" added successfully.')
                return redirect('customer_list')
            else:
                messages.error(request, 'Please fill in all required fields.')
    
    customers = Customer.objects.select_related('street').all()
    streets = Street.objects.all()
    
    # Calculate customer stats
    total_customers = customers.count()
    customers_with_units = customers.filter(total_units__gt=0).count()
    customers_without_units = customers.filter(total_units=0).count()
    
    return render(request, 'customers.html', {
        'customers': customers,
        'streets': streets,
        'active_page': 'customers',
        'total_customers': total_customers,
        'customers_with_units': customers_with_units,
        'customers_without_units': customers_without_units,
    })


@login_required(login_url='login')
def street_list(request):
    if request.user.role not in ['manager', 'staff']:
        return redirect('login')
    
    if request.method == 'POST':
        region = request.POST.get('region')
        district = request.POST.get('district')
        street_name = request.POST.get('street_name')
        
        if region and district and street_name:
            Street.objects.get_or_create(
                region=region,
                district=district,
                street_name=street_name
            )
            messages.success(request, f'Street "{street_name}" added successfully.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('street_list')
    
    streets = Street.objects.all()
    return render(request, 'streets.html', {
        'streets': streets,
        'active_page': 'streets'
    })
