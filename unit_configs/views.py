from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UnitConfig

# Create your views here.

@login_required(login_url='login')
def unit_config_list(request):
    if request.user.role != 'manager':
        return redirect('login')
    
    if request.method == 'POST':
        unit = request.POST.get('unit')
        price_per_unit = request.POST.get('price_per_unit')
        
        if unit and price_per_unit:
            UnitConfig.objects.create(
                unit=unit,
                price_per_unit=price_per_unit,
                total_amount=float(unit) * float(price_per_unit),
                is_active=True
            )
            messages.success(request, 'Unit configuration added successfully.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('unit_config_list')
    
    unit_configs = UnitConfig.objects.all()
    return render(request, 'unit_configs.html', {
        'unit_configs': unit_configs,
        'active_page': 'unit_configs'
    })


@login_required(login_url='login')
def toggle_unit_config(request, config_id):
    if request.user.role != 'manager':
        return redirect('login')
    
    config = get_object_or_404(UnitConfig, id=config_id)
    
    if config.is_active:
        # Deactivate
        config.is_active = False
        config.save()
        messages.success(request, f'Unit configuration deactivated.')
    else:
        # Activate - deactivate all others first
        UnitConfig.objects.filter(is_active=True).update(is_active=False)
        config.is_active = True
        config.save()
        messages.success(request, f'Unit configuration activated.')
    
    return redirect('unit_config_list')
