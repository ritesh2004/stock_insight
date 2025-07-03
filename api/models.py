from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.

class StockInsight(models.Model):
    stock_symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=255)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    market_cap = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.stock_symbol} - {self.company_name}"
    
    class Meta:
        verbose_name = "Stock Insight"
        verbose_name_plural = "Stock Insights"


class StockPrediction(models.Model):
    """
    Model to store stock prediction results with metrics and plot file paths
    """
    # Basic prediction info
    stock_symbol = models.CharField(max_length=10, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    
    # Prediction results
    next_day_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Model performance metrics
    mse = models.FloatField(help_text="Mean Squared Error")
    rmse = models.FloatField(help_text="Root Mean Squared Error")
    r2 = models.FloatField(help_text="R-squared Score")
    
    # Additional metrics as JSON field for flexibility
    metrics_json = models.JSONField(
        default=dict,
        help_text="Additional metrics and model parameters in JSON format"
    )
    
    # Plot file paths
    plot_urls = models.JSONField(
        default=list,
        help_text="List of URLs/paths to generated PNG plots"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional: Store the actual stock price for comparison later
    actual_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Actual stock price for validation (filled later)"
    )
    
    def __str__(self):
        return f"{self.stock_symbol} - {self.next_day_price} (Predicted on {self.created_at.date()})"
    

class TelegramUser(models.Model):
    """
    Model to store Telegram user information and manage bot interactions
    """
    # Link to Django User (required for /start command)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='telegram_user',
        help_text="Linked Django user account"
    )
    
    # Telegram user information
    chat_id = models.BigIntegerField(unique=True, db_index=True, help_text="Telegram chat ID")
    telegram_user_id = models.BigIntegerField(help_text="Telegram user ID")
    username = models.CharField(max_length=255, blank=True, null=True, help_text="Telegram username")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
       return f"{self.username or 'Unknown'} ({self.chat_id})"
   