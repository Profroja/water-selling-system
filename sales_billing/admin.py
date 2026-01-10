from django.contrib import admin
from .models import Order, Expenditure

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'receipt_number', 'customer', 'street', 'units', 'unit_price', 'total_amount', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'created_at', 'street')
    search_fields = ('order_number', 'receipt_number', 'customer__first_name', 'customer__last_name')
    readonly_fields = ('order_number', 'receipt_number')


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'purpose', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('purpose',)
