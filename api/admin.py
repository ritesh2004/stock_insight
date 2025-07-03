from django.contrib import admin
from .models import StockPrediction, TelegramUser

# Register your models here.

@admin.register(StockPrediction)
class StockPredictionAdmin(admin.ModelAdmin):
    list_display = ('stock_symbol', 'user', 'next_day_price', 'metrics_json', 'plot_urls', 'created_at')
    list_filter = ('stock_symbol', 'created_at', 'user')
    search_fields = ('stock_symbol', 'user')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'user', 'chat_id', 'telegram_user_id', 'created_at')
    search_fields = ('username', 'chat_id')
    readonly_fields = ('created_at', 'updated_at', 'telegram_user_id', 'chat_id')
