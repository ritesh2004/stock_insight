from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterUserForm, LoginUserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from api.models import StockPrediction
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# For stripe payments
from django.conf import settings
import stripe
from django.contrib.auth.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

from api.models import UserProfile, TelegramUser
def get_or_create_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile

def get_or_create_telegram_user(user):
    profile, created = TelegramUser.objects.get_or_create(user=user)
    return profile

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
    user = request.user 
    profile = get_or_create_user_profile(user)
    # Pagination
    paginator = Paginator(past_predictions, 10)  # Show 10 predictions per page
    page_number = request.GET.get('page')
    try:
        past_predictions = paginator.get_page(page_number)
    except PageNotAnInteger:
        past_predictions = paginator.get_page(1)
    except EmptyPage:
        past_predictions = paginator.get_page(paginator.num_pages)
    return render(request, 'dashboard.html', {'user': profile, 'past_predictions': past_predictions })


@csrf_exempt
def create_checkout_session(request):
    """Create a Stripe checkout session."""
    user = request.user
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': 'Premium Stock Prediction Service',
                    },
                    'unit_amount': 19900,  # $5.00
                    "recurring": {
                        "interval": "month",
                    }
                },
                'quantity': 1,
            },
        ],
        mode='subscription',
        success_url=request.build_absolute_uri('/'),
        cancel_url=request.build_absolute_uri('/'),
        metadata={
            'user_id': user.id,
        },
    )
    return redirect(checkout_session.url, code=303)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'checkout.session.completed':
        user_id = event['data']['object']['metadata'].get('user_id')
        chat_id = event['data']['object']['metadata'].get('chat_id')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                profile = get_or_create_user_profile(user)
                profile.is_pro = True
                profile.save()
                return JsonResponse({'status':'ok'})
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
        
        elif chat_id:
            try:
                telegram_user = TelegramUser.objects.get(chat_id=chat_id)
                telegram_user.is_pro = True
                telegram_user.save()
                return JsonResponse({'status': 'ok'})
            except TelegramUser.DoesNotExist:
                return JsonResponse({'error': 'Telegram user not found'}, status=404)

    return JsonResponse({'status': 'ok'})

    