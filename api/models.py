from django.db import models
from django.contrib.auth.models import User
import json

# Create your models here.

class UserProfile(models.Model):
    """
    Model to store additional user information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_pro = models.BooleanField(default=False, help_text="Indicates if the user has a premium account")
    daily_request_count = models.PositiveIntegerField(default=0, help_text="Count of daily prediction requests made by the user")
    last_request_date = models.DateField(auto_now_add=True, help_text="Date of the last prediction request made by the user")

    def __str__(self):
        return f"{self.user.username} Profile"

class StockPrediction(models.Model):
    """
    Model to store stock prediction results with metrics and plot file paths
    """
    # Basic prediction info
    stock_symbol = models.CharField(max_length=10, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    
    # Prediction results
    next_day_price = models.DecimalField(max_digits=10, decimal_places=2)
    
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
    username = models.CharField(max_length=255, blank=True, null=True, help_text="Telegram username")
    is_pro = models.BooleanField(default=False, help_text="Indicates if the user has a premium account")
    daily_request_count = models.PositiveIntegerField(default=0, help_text="Count of daily prediction requests made by the user")
    last_request_date = models.DateField(auto_now_add=True, help_text="Date of the last prediction request made by the user")
    
    def __str__(self):
       return f"{self.username or 'Unknown'} ({self.chat_id})"
   