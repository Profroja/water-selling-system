from django.db import models
from django.utils import timezone
from customers.models import Customer, Street
from unit_configs.models import UnitConfig
import uuid
import random
import string

# Create your models here.

class Order(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('debt', 'Debt'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    receipt_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True, related_name='orders')
    units = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    created_by = models.ForeignKey('auths.CustomUser', on_delete=models.SET_NULL, null=True, related_name='orders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_order_number():
        prefix = 'ORD'
        timestamp = timezone.now().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"
    
    @staticmethod
    def generate_receipt_number():
        prefix = 'RCP'
        timestamp = timezone.now().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}{timestamp}{random_suffix}"
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer}"
    
    class Meta:
        ordering = ['-created_at']


class Expenditure(models.Model):
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField()
    created_by = models.ForeignKey('auths.CustomUser', on_delete=models.SET_NULL, null=True, related_name='expenditures_created')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Expenditure: TZS {self.amount} - {self.purpose[:50]}"
    
    class Meta:
        ordering = ['-created_at']


class CustomReportEntry(models.Model):
    """Custom report entries for historical data that can be manually entered"""
    mwaka = models.CharField(max_length=50, help_text="Year range e.g. '2016 - 2018'")
    mwezi = models.CharField(max_length=100, help_text="Month range e.g. 'Feb. 2016 - Dec. 2022'")
    units_sold = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    expenditure = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey('auths.CustomUser', on_delete=models.SET_NULL, null=True, related_name='custom_reports_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def profit(self):
        return self.sales - self.expenditure
    
    def __str__(self):
        return f"Report: {self.mwaka} - {self.mwezi}"
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Custom Report Entry"
        verbose_name_plural = "Custom Report Entries"
