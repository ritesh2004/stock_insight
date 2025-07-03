from django.shortcuts import render

# Viewsets and generic views for the API
from rest_framework import viewsets
from rest_framework import generics

# Model and Serializer imports
from django.contrib.auth.models import User
from .models import StockPrediction, StockInsight, TelegramUser
from .serializers import StockPredictionSerializer, StockInsightSerializer, TelegramUserSerializer, RegisterUserSerializer, UserSerializer

# Permission classes
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.

# Viewset for Registering new users
class RegisterUserView(generics.CreateAPIView):
    """View to register new users via API
    """
    serializer_class = RegisterUserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    
# Viewset for User details
class UserDetailView(generics.RetrieveUpdateAPIView):
    """View to retrieve and update user details
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
# Viewset for Stock Insights
class StockInsightViewSet(viewsets.ModelViewSet):
    """Viewset for Stock Insights
    """
    queryset = StockInsight.objects.all()
    serializer_class = StockInsightSerializer
    permission_classes = [IsAuthenticated]
    
# Viewset for Stock Predictions
class StockPredictionViewSet(viewsets.ModelViewSet):
    """Viewset for Stock Predictions
    """
    queryset = StockPrediction.objects.all()
    serializer_class = StockPredictionSerializer
    permission_classes = [IsAuthenticated]
    
# Viewset for Telegram Users
class TelegramUserViewSet(viewsets.ModelViewSet):
    """Viewset for managing Telegram users
    """
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated]
    
    
