from django.contrib import admin
from .models import StockPrediction, TelegramUser, UserProfile

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
    list_display = ('username', 'user', 'chat_id', 'is_pro', 'daily_request_count', 'last_request_date')
    search_fields = ('username', 'chat_id')
    readonly_fields = ('chat_id', 'user')
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_pro', 'daily_request_count', 'last_request_date')
    search_fields = ('user__username',)
    readonly_fields = ('user',)