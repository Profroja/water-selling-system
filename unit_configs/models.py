from django.db import models
from decimal import Decimal

# Create your models here.

class UnitConfig(models.Model):
    unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Number of units (e.g., liters)")
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total amount (unit * price)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_amount = Decimal(str(self.unit)) * Decimal(str(self.price_per_unit))
        if self.is_active:
            UnitConfig.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.unit} units @ {self.price_per_unit} = {self.total_amount}"

    class Meta:
        ordering = ['-created_at']
