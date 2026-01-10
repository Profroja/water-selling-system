from django.db import models

# Create your models here.

class Street(models.Model):
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street_name} - {self.district}, {self.region}"

    class Meta:
        ordering = ['region', 'district', 'street_name']
        unique_together = ['region', 'district', 'street_name']


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    street = models.ForeignKey(Street, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')
    total_units = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-created_at']


class CustomerDebt(models.Model):
    """Track customer debts for water units"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debts')
    order = models.OneToOneField('sales_billing.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='debt')
    units = models.DecimalField(max_digits=10, decimal_places=2, help_text="Units of water owed")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total debt amount in TZS")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Amount paid so far")
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_by = models.ForeignKey('auths.CustomUser', on_delete=models.SET_NULL, null=True, related_name='debts_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def remaining_amount(self):
        """Calculate remaining debt amount"""
        return self.amount - self.amount_paid
    
    @property
    def order_number(self):
        """Get order number if linked to an order"""
        return self.order.order_number if self.order else None

    def __str__(self):
        return f"{self.customer} - TZS {self.amount} ({self.units} units)"

    class Meta:
        ordering = ['-created_at']


class DebtPayment(models.Model):
    """Track individual payments made towards a debt"""
    debt = models.ForeignKey(CustomerDebt, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey('auths.CustomUser', on_delete=models.SET_NULL, null=True, related_name='debt_payments_received')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of TZS {self.amount} for {self.debt.customer}"

    class Meta:
        ordering = ['-created_at']
