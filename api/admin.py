from django.contrib import admin
from .models import StockInsight, StockPrediction, TelegramUser

# Register your models here.

@admin.register(StockInsight)
class StockInsightAdmin(admin.ModelAdmin):
    list_display = ('stock_symbol', 'company_name', 'current_price', 'market_cap', 'volume', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('stock_symbol', 'company_name')
    readonly_fields = ('last_updated',)


@admin.register(StockPrediction)
class StockPredictionAdmin(admin.ModelAdmin):
    list_display = ('stock_symbol', 'user', 'next_day_price', 'mse', 'rmse', 'r2', 'created_at')
    list_filter = ('stock_symbol', 'created_at', 'user')
    search_fields = ('stock_symbol', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('stock_symbol', 'user', 'next_day_price')
        }),
        ('Model Metrics', {
            'fields': ('mse', 'rmse', 'r2', 'metrics_json')
        }),
        ('Plots and Validation', {
            'fields': ('plot_urls', 'actual_price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'user', 'chat_id', 'telegram_user_id', 'created_at')
    search_fields = ('username', 'chat_id')
    readonly_fields = ('created_at', 'updated_at', 'telegram_user_id', 'chat_id')
