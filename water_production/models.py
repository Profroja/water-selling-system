from django.db import models
from django.utils import timezone
from decimal import Decimal

# Create your models here.

class WaterProduction(models.Model):
    """Track daily water production and inventory"""
    date = models.DateField(unique=True, default=timezone.now)
    units_produced = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Units produced on this day")
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about production")
    user = models.ForeignKey('auths.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='water_productions', help_text="User who entered this record")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def units_sold(self):
        """Calculate total units sold from orders on this date"""
        from sales_billing.models import Order
        total = Order.objects.filter(
            created_at__date=self.date
        ).aggregate(total=models.Sum('units'))['total']
        return total or Decimal('0')
    
    @property
    def units_remaining(self):
        """Calculate remaining units (produced - sold)"""
        return self.units_produced - self.units_sold
    
    @classmethod
    def get_total_stock(cls):
        """Get total available stock across all production days"""
        from sales_billing.models import Order
        total_produced = cls.objects.aggregate(total=models.Sum('units_produced'))['total'] or Decimal('0')
        total_sold = Order.objects.aggregate(total=models.Sum('units'))['total'] or Decimal('0')
        return total_produced - total_sold
    
    def __str__(self):
        return f"Production {self.date}: {self.units_produced} units"
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Water Production"
        verbose_name_plural = "Water Productions"
