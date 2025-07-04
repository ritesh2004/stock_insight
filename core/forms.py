from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from api.models import StockPrediction

class RegisterUserForm(UserCreationForm):
    """Form for user registration."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
class LoginUserForm(AuthenticationForm):
    """Form for user login."""
    username = forms.CharField(label='Username', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
class PredictionForm(forms.Form):
    """Form for stock prediction input."""
    stock_symbol = forms.CharField(label='Stock Symbol', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        fields = ['stock_symbol', 'created_at']
        model = StockPrediction