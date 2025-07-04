from django.urls import path
from .views import register_view, login_view, logout_view, dashboard_view, create_checkout_session, stripe_webhook

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard_view, name='dashboard'),
    path('checkout/', create_checkout_session, name='create_checkout_session'),
    path('webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
]