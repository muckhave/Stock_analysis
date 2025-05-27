from django.contrib import admin
from .models import OptimizationResult

@admin.register(OptimizationResult)
class OptimizationResultAdmin(admin.ModelAdmin):
    list_display = ("ticker", "strategy_name", "interval", "created_at")
