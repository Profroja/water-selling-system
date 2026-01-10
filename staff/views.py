from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from customers.models import Customer, Street, CustomerDebt, DebtPayment
from unit_configs.models import UnitConfig
from sales_billing.models import Order, Expenditure
from water_production.models import WaterProduction

# Create your views here.

@login_required(login_url='login')
def staff_dashboard(request):
    if request.user.role != 'staff':
        return redirect('login')
    
    # Get week offset from query params (0 = current week, 1 = last week, etc.)
    week_offset = int(request.GET.get('week', 0))
    
    # Calculate week start and end based on offset
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday())  # Monday of current week
    week_start = current_week_start - timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)  # Sunday
    
    # Get ISO week number and year
    week_number = week_start.isocalendar()[1]
    year = week_start.isocalendar()[0]
    
    # Get orders for the selected week
    orders = Order.objects.filter(
        created_at__date__gte=week_start,
        created_at__date__lte=week_end
    )
    order_stats = orders.aggregate(
        total_units=Sum('units'),
        total_sales=Sum('total_amount')
    )
    total_units = order_stats['total_units'] or 0
    total_sales = order_stats['total_sales'] or 0
    total_orders = orders.count()
    
    # Get expenditure for the selected week
    expenditures = Expenditure.objects.filter(
        created_at__date__gte=week_start,
        created_at__date__lte=week_end
    )
    expenditure_total = expenditures.aggregate(total=Sum('amount'))
    total_expenditure = expenditure_total['total'] or 0
    
    # Calculate profit
    profit = total_sales - total_expenditure
    
    return render(request, 'staff_dashboard.html', {
        'active_page': 'dashboard',
        'week_offset': week_offset,
        'week_number': week_number,
        'year': year,
        'week_start': week_start,
        'week_end': week_end,
        'total_units': total_units,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_expenditure': total_expenditure,
        'profit': profit,
    })


@login_required(login_url='login')
def order_list(request):
    if request.user.role != 'staff':
        return redirect('login')
    
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        street_id = request.POST.get('street')
        units = request.POST.get('units')
        payment_method = request.POST.get('payment_method')
        
        if customer_id and street_id and units and payment_method:
            # Check available stock first
            available_stock = WaterProduction.get_total_stock()
            requested_units = Decimal(units)
            
            if requested_units > available_stock:
                messages.error(request, f'Hakuna maji ya kutosha! Unaomba units {requested_units}, lakini zipo units {available_stock} tu.')
                return redirect('order_list')
            
            customer = Customer.objects.get(id=customer_id)
            street = Street.objects.get(id=street_id)
            
            # Get active unit config for price
            active_config = UnitConfig.objects.filter(is_active=True).first()
            if active_config:
                unit_price = active_config.price_per_unit
                total_amount = Decimal(units) * unit_price
                
                Order.objects.create(
                    customer=customer,
                    street=street,
                    units=units,
                    unit_price=unit_price,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    created_by=request.user
                )
                
                # Update customer total units
                customer.total_units = (customer.total_units or 0) + Decimal(units)
                customer.save()
                
                messages.success(request, 'Order created successfully.')
            else:
                messages.error(request, 'No active unit configuration found. Please contact manager.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('order_list')
    
    orders = Order.objects.select_related('customer', 'street').all()
    streets = Street.objects.all()
    customers = Customer.objects.select_related('street').all()
    active_config = UnitConfig.objects.filter(is_active=True).first()
    available_stock = WaterProduction.get_total_stock()
    
    return render(request, 'orders.html', {
        'orders': orders,
        'streets': streets,
        'customers': customers,
        'active_config': active_config,
        'available_stock': available_stock,
        'active_page': 'orders'
    })


@login_required(login_url='login')
def get_customers_by_street(request):
    if request.user.role != 'staff':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    street_id = request.GET.get('street_id')
    if street_id:
        customers = Customer.objects.filter(street_id=street_id).values('id', 'first_name', 'last_name')
        return JsonResponse({'customers': list(customers)})
    return JsonResponse({'customers': []})


@login_required(login_url='login')
def sales_list(request):
    if request.user.role != 'staff':
        return redirect('login')
    
    # Get week filter from query param
    week_filter = request.GET.get('week', 'all')
    
    # Calculate available weeks
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday())
    weeks = []
    for i in range(12):  # Last 12 weeks
        week_start = current_week_start - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_num = week_start.isocalendar()[1]
        weeks.append({
            'value': i,
            'label': f"Week {week_num} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')})",
            'start': week_start,
            'end': week_end
        })
    
    # Filter orders based on week
    if week_filter != 'all':
        try:
            week_idx = int(week_filter)
            week_start = current_week_start - timedelta(weeks=week_idx)
            week_end = week_start + timedelta(days=6)
            orders = Order.objects.filter(
                created_at__date__gte=week_start,
                created_at__date__lte=week_end
            ).select_related('customer', 'street', 'created_by').order_by('-created_at')
        except ValueError:
            orders = Order.objects.select_related('customer', 'street', 'created_by').all().order_by('-created_at')
    else:
        orders = Order.objects.select_related('customer', 'street', 'created_by').all().order_by('-created_at')
    
    # Calculate totals
    totals = orders.aggregate(
        total_units=Sum('units'),
        total_revenue=Sum('total_amount')
    )
    
    return render(request, 'sales.html', {
        'orders': orders,
        'total_units': totals['total_units'] or 0,
        'total_revenue': totals['total_revenue'] or 0,
        'active_page': 'sales',
        'weeks': weeks,
        'selected_week': week_filter
    })


@login_required(login_url='login')
def expenditure_list(request):
    if request.user.role != 'staff':
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete':
            expenditure_id = request.POST.get('expenditure_id')
            try:
                expenditure = Expenditure.objects.get(id=expenditure_id)
                expenditure.delete()
                messages.success(request, 'Expenditure deleted successfully.')
            except Expenditure.DoesNotExist:
                messages.error(request, 'Expenditure not found.')
            return redirect('expenditure_list')
        
        # Add new expenditure
        date = request.POST.get('date')
        amount = request.POST.get('amount')
        purpose = request.POST.get('purpose')
        
        if date and amount and purpose:
            Expenditure.objects.create(
                date=date,
                amount=amount,
                purpose=purpose,
                created_by=request.user
            )
            messages.success(request, 'Expenditure added successfully.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('expenditure_list')
    
    # Get week filter from query param
    week_filter = request.GET.get('week', 'all')
    
    # Calculate available weeks
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday())
    weeks = []
    for i in range(12):  # Last 12 weeks
        week_start = current_week_start - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_num = week_start.isocalendar()[1]
        weeks.append({
            'value': i,
            'label': f"Week {week_num} ({week_start.strftime('%b %d')} - {week_end.strftime('%b %d')})",
            'start': week_start,
            'end': week_end
        })
    
    # Filter expenditures based on week
    if week_filter != 'all':
        try:
            week_idx = int(week_filter)
            week_start = current_week_start - timedelta(weeks=week_idx)
            week_end = week_start + timedelta(days=6)
            expenditures = Expenditure.objects.filter(
                date__gte=week_start,
                date__lte=week_end
            ).order_by('-created_at')
        except ValueError:
            expenditures = Expenditure.objects.all().order_by('-created_at')
    else:
        expenditures = Expenditure.objects.all().order_by('-created_at')
    
    # Calculate totals (based on filtered data)
    # Only count paid orders (exclude debt) for available amount
    total_revenue = Order.objects.exclude(payment_method='debt').aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    total_debt = Order.objects.filter(payment_method='debt').aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    # Add debt payments received to total revenue
    total_debt_payments = DebtPayment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_income = total_revenue + total_debt_payments
    total_expenditure = expenditures.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    amount_available = total_income - total_expenditure
    
    return render(request, 'expenditure.html', {
        'expenditures': expenditures,
        'total_revenue': total_revenue,
        'total_debt_payments': total_debt_payments,
        'total_income': total_income,
        'total_expenditure': total_expenditure,
        'amount_available': amount_available,
        'active_page': 'expenditure',
        'weeks': weeks,
        'selected_week': week_filter
    })


@login_required(login_url='login')
def weekly_report(request):
    if request.user.role != 'staff':
        return redirect('login')
    
    # Get week number from query param, default to current week
    week_offset = int(request.GET.get('week', 0))
    
    # Calculate current week's Monday
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday())
    
    # Apply week offset (negative for past weeks)
    week_start = current_week_start - timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)
    
    # Calculate week number of the year
    week_number = week_start.isocalendar()[1]
    year = week_start.year
    
    # Get orders for this week
    weekly_orders = Order.objects.filter(
        created_at__date__gte=week_start,
        created_at__date__lte=week_end
    ).select_related('customer', 'street', 'created_by').order_by('-created_at')
    
    # Calculate order stats (all orders including debt)
    order_stats = weekly_orders.aggregate(
        total_units=Sum('units'),
        total_amount=Sum('total_amount')
    )
    total_units = order_stats['total_units'] or 0
    total_sales = order_stats['total_amount'] or 0
    total_orders = weekly_orders.count()
    
    # Calculate paid sales (exclude debt orders for profit calculation)
    paid_orders = weekly_orders.exclude(payment_method='debt')
    paid_sales_stats = paid_orders.aggregate(total_amount=Sum('total_amount'))
    paid_sales = paid_sales_stats['total_amount'] or Decimal('0')
    
    # Calculate debt sales for this week
    debt_orders = weekly_orders.filter(payment_method='debt')
    debt_sales_stats = debt_orders.aggregate(total_amount=Sum('total_amount'))
    total_debt_sales = debt_sales_stats['total_amount'] or Decimal('0')
    
    # Get debt payments received this week (from previous debts)
    debt_payments_this_week = DebtPayment.objects.filter(
        payment_date__gte=week_start,
        payment_date__lte=week_end
    ).aggregate(total=Sum('amount'))
    debt_payments_received = debt_payments_this_week['total'] or Decimal('0')
    
    # Get expenditures for this week
    weekly_expenditures = Expenditure.objects.filter(
        date__gte=week_start,
        date__lte=week_end
    ).aggregate(total=Sum('amount'))
    total_expenditure = weekly_expenditures['total'] or Decimal('0')
    
    # Calculate total income (paid sales + debt payments received)
    total_income = paid_sales + debt_payments_received
    
    # Calculate profit (paid sales + debt payments - expenditure)
    profit = total_income - total_expenditure
    
    return render(request, 'weekly_report.html', {
        'active_page': 'reports',
        'week_offset': week_offset,
        'week_number': week_number,
        'year': year,
        'week_start': week_start,
        'week_end': week_end,
        'total_units': total_units,
        'total_sales': total_sales,
        'paid_sales': paid_sales,
        'total_debt_sales': total_debt_sales,
        'debt_payments_received': debt_payments_received,
        'total_income': total_income,
        'total_orders': total_orders,
        'total_expenditure': total_expenditure,
        'profit': profit,
        'orders': weekly_orders,
    })


@login_required(login_url='login')
def water_production_list(request):
    if request.user.role != 'staff':
        return redirect('login')
    
    if request.method == 'POST':
        date = request.POST.get('date')
        units_produced = request.POST.get('units_produced')
        notes = request.POST.get('notes', '')
        
        if date and units_produced:
            try:
                production, created = WaterProduction.objects.update_or_create(
                    date=date,
                    defaults={
                        'units_produced': Decimal(units_produced),
                        'notes': notes,
                        'user': request.user
                    }
                )
                if created:
                    messages.success(request, f'Production record for {date} added successfully.')
                else:
                    messages.success(request, f'Production record for {date} updated successfully.')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('water_production_list')
    
    # Get filter parameters
    selected_month = request.GET.get('month', '')
    selected_year = request.GET.get('year', '')
    
    # Get all production records
    productions = WaterProduction.objects.all()
    
    # Apply month/year filter if provided
    if selected_month and selected_year:
        productions = productions.filter(
            date__month=int(selected_month),
            date__year=int(selected_year)
        )
    elif selected_year:
        productions = productions.filter(date__year=int(selected_year))
    
    # Calculate totals (filtered)
    total_produced = productions.aggregate(total=Sum('units_produced'))['total'] or Decimal('0')
    
    # Calculate sold units for the filtered period
    if selected_month and selected_year:
        total_sold = Order.objects.filter(
            created_at__month=int(selected_month),
            created_at__year=int(selected_year)
        ).aggregate(total=Sum('units'))['total'] or Decimal('0')
    elif selected_year:
        total_sold = Order.objects.filter(
            created_at__year=int(selected_year)
        ).aggregate(total=Sum('units'))['total'] or Decimal('0')
    else:
        total_sold = Order.objects.aggregate(total=Sum('units'))['total'] or Decimal('0')
    
    total_remaining = total_produced - total_sold
    
    # Get available years for filter dropdown
    available_years = WaterProduction.objects.dates('date', 'year', order='DESC')
    years = [d.year for d in available_years]
    if not years:
        years = [timezone.now().year]
    
    # Months list
    months = [
        (1, 'Januari'), (2, 'Februari'), (3, 'Machi'), (4, 'Aprili'),
        (5, 'Mei'), (6, 'Juni'), (7, 'Julai'), (8, 'Agosti'),
        (9, 'Septemba'), (10, 'Oktoba'), (11, 'Novemba'), (12, 'Desemba')
    ]
    
    return render(request, 'water_production.html', {
        'active_page': 'water_production',
        'productions': productions,
        'total_produced': total_produced,
        'total_sold': total_sold,
        'total_remaining': total_remaining,
        'months': months,
        'years': years,
        'selected_month': selected_month,
        'selected_year': selected_year,
    })


@login_required(login_url='login')
def customer_debts_list(request):
    if request.user.role != 'staff':
        return redirect('login')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'delete':
            debt_id = request.POST.get('debt_id')
            try:
                debt = CustomerDebt.objects.get(id=debt_id)
                debt.delete()
                messages.success(request, 'Deni limefutwa.')
            except CustomerDebt.DoesNotExist:
                messages.error(request, 'Deni halipatikani.')
            return redirect('customer_debts_list')
        
        if action == 'pay':
            debt_id = request.POST.get('debt_id')
            payment_amount = request.POST.get('payment_amount')
            try:
                debt = CustomerDebt.objects.get(id=debt_id)
                payment_decimal = Decimal(payment_amount)
                
                # Create payment record in history
                DebtPayment.objects.create(
                    debt=debt,
                    amount=payment_decimal,
                    received_by=request.user
                )
                
                # Update debt amount_paid
                debt.amount_paid += payment_decimal
                if debt.amount_paid >= debt.amount:
                    debt.is_paid = True
                debt.save()
                messages.success(request, 'Malipo yamerekodiwa.')
            except CustomerDebt.DoesNotExist:
                messages.error(request, 'Deni halipatikani.')
            return redirect('customer_debts_list')
        
        # Add new debt
        customer_id = request.POST.get('customer')
        units = request.POST.get('units')
        amount = request.POST.get('amount')
        
        if customer_id and units and amount:
            try:
                customer = Customer.objects.get(id=customer_id)
                units_decimal = Decimal(units)
                amount_decimal = Decimal(amount)
                
                # Get active unit config for price
                active_config = UnitConfig.objects.filter(is_active=True).first()
                unit_price = active_config.price_per_unit if active_config else Decimal('5000')
                
                # Create the Order first (like a credit sale)
                order = Order.objects.create(
                    customer=customer,
                    street=customer.street,
                    units=units_decimal,
                    unit_price=unit_price,
                    total_amount=amount_decimal,
                    payment_method='debt',
                    created_by=request.user
                )
                
                # Create the debt record linked to the order
                CustomerDebt.objects.create(
                    customer=customer,
                    order=order,
                    units=units_decimal,
                    amount=amount_decimal,
                    created_by=request.user
                )
                
                # Update customer's total units (like an order)
                customer.total_units += units_decimal
                customer.save()
                
                messages.success(request, f'Deni limeongezwa. Order: {order.order_number}')
            except Customer.DoesNotExist:
                messages.error(request, 'Mteja hapatikani.')
        else:
            messages.error(request, 'Tafadhali jaza sehemu zote.')
        return redirect('customer_debts_list')
    
    # Get all debts with order info
    debts = CustomerDebt.objects.select_related('customer', 'customer__street', 'order').prefetch_related('payments').all()
    
    # Calculate totals
    total_debts = debts.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_units_debt = debts.aggregate(total=Sum('units'))['total'] or Decimal('0')
    total_paid = debts.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
    total_remaining = total_debts - total_paid
    
    # Get customers for dropdown
    customers = Customer.objects.filter(is_active=True).order_by('first_name')
    
    # Get active unit config for price calculation
    active_config = UnitConfig.objects.filter(is_active=True).first()
    price_per_unit = active_config.price_per_unit if active_config else Decimal('5000')
    
    # Get available stock
    available_stock = WaterProduction.get_total_stock()
    
    return render(request, 'customer_debts.html', {
        'active_page': 'customer_debts',
        'debts': debts,
        'total_debts': total_debts,
        'total_units_debt': total_units_debt,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
        'customers': customers,
        'price_per_unit': price_per_unit,
        'available_stock': available_stock,
    })


@login_required(login_url='login')
def get_debt_payments(request, debt_id):
    """API endpoint to get payment history for a debt"""
    if request.user.role != 'staff':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        debt = CustomerDebt.objects.get(id=debt_id)
        payments = DebtPayment.objects.filter(debt=debt).order_by('-payment_date')
        
        payment_list = []
        for payment in payments:
            payment_list.append({
                'amount': float(payment.amount),
                'date': payment.payment_date.strftime('%d %b, %Y'),
                'received_by': payment.received_by.username if payment.received_by else '-',
                'notes': payment.notes or '-'
            })
        
        return JsonResponse({
            'payments': payment_list,
            'total_paid': float(debt.amount_paid),
            'total_debt': float(debt.amount),
            'remaining': float(debt.remaining_amount)
        })
    except CustomerDebt.DoesNotExist:
        return JsonResponse({'error': 'Debt not found'}, status=404)
