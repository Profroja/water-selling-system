from django.contrib import admin
from .models import UnitConfig

# Register your models here.

@admin.register(UnitConfig)
class UnitConfigAdmin(admin.ModelAdmin):
    list_display = ('unit', 'price_per_unit', 'total_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('unit', 'price_per_unit')
