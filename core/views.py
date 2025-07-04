from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterUserForm, LoginUserForm, PredictionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from api.models import StockPrediction
from ml_model.predict_utils import predict_with_plot, fetch_ohlcv_data
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def register_view(request):
    """Render the registration page."""
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterUserForm()
        
    return render(request, 'register.html', {'form': form})

def login_view(request):
    """Render the login page."""
    if request.method == 'POST':
        form = LoginUserForm(request=request ,data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginUserForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')

@csrf_exempt
@login_required(login_url='login')
def dashboard_view(request):
    """Render the dashboard page."""
    past_predictions = StockPrediction.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(past_predictions, 10)  # Show 10 predictions per page
    page_number = request.GET.get('page')
    try:
        past_predictions = paginator.get_page(page_number)
    except PageNotAnInteger:
        past_predictions = paginator.get_page(1)
    except EmptyPage:
        past_predictions = paginator.get_page(paginator.num_pages)
    return render(request, 'dashboard.html', {'user': request.user, 'past_predictions': past_predictions })