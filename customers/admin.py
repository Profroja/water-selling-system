from django.contrib import admin
from .models import Customer, Street, CustomerDebt, DebtPayment

# Register your models here.

@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    list_display = ('street_name', 'district', 'region')
    list_filter = ('region', 'district')
    search_fields = ('street_name', 'district', 'region')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'street', 'total_units', 'is_active')
    list_filter = ('street', 'is_active')
    search_fields = ('first_name', 'last_name', 'phone_number')


@admin.register(CustomerDebt)
class CustomerDebtAdmin(admin.ModelAdmin):
    list_display = ('customer', 'order_number', 'units', 'amount', 'amount_paid', 'remaining_amount', 'is_paid', 'date')
    list_filter = ('is_paid', 'date')
    search_fields = ('customer__first_name', 'customer__last_name', 'description', 'order__order_number')


@admin.register(DebtPayment)
class DebtPaymentAdmin(admin.ModelAdmin):
    list_display = ('debt', 'amount', 'payment_date', 'received_by')
    list_filter = ('payment_date',)
    search_fields = ('debt__customer__first_name', 'debt__customer__last_name', 'notes')
