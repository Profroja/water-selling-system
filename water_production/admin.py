from django.contrib import admin
from .models import WaterProduction

# Register your models here.

@admin.register(WaterProduction)
class WaterProductionAdmin(admin.ModelAdmin):
    list_display = ('date', 'units_produced', 'units_sold', 'units_remaining', 'notes', 'created_at')
    list_filter = ('date',)
    search_fields = ('notes',)
    ordering = ('-date',)
    date_hierarchy = 'date'
