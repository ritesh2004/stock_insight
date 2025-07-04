from django.shortcuts import render

# Viewsets and generic views for the API
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

# Model and Serializer imports
from django.contrib.auth.models import User
from .models import StockPrediction, TelegramUser, UserProfile
from .serializers import StockPredictionSerializer, TelegramUserSerializer, RegisterUserSerializer, UserSerializer

from datetime import date

# Permission classes
from rest_framework.permissions import IsAuthenticated, AllowAny

# ML model utilities
from ml_model.predict_utils import fetch_ohlcv_data, predict_with_plot

# Django filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# Create your views here.

def get_or_create_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile

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
    
    
# Viewset for Stock Predictions
class StockPredictionViewSet(viewsets.ModelViewSet):
    """Viewset for Stock Predictions
    """
    queryset = StockPrediction.objects.all()
    serializer_class = StockPredictionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['stock_symbol', 'user']
    ordering_fields = ['created_at', 'stock_symbol']
    ordering = ['-created_at']
    
    def create(self, request, *args, **kwargs):
        """Override create method to handle custom logic if needed
        """
        try:
            user = request.user
            profile = get_or_create_user_profile(user)

            # Reset count if new day
            if profile.last_request_date != date.today():
                profile.daily_request_count = 0
                profile.last_request_date = date.today()

            if not profile.is_pro and profile.daily_request_count >= 5:
                return Response({'error': 'Quota exceeded. Upgrade to Pro.'}, status=429)

            # Count this request
            profile.daily_request_count += 1
            profile.save()
            ticker = request.data.get('ticker')
            df = fetch_ohlcv_data(ticker)
            if df.empty:
                return Response({"error": "No data found for the ticker"}, status=status.HTTP_400_BAD_REQUEST)
            prediction_result = predict_with_plot(df, ticker)
            
            StockPrediction.objects.create(
                stock_symbol=ticker,
                user=request.user,
                next_day_price=prediction_result['next_day_price'],
                plot_urls=prediction_result['plot_urls'],
                metrics_json=prediction_result['metrics']
            )
            
            return Response(
                {"message": "Prediction created successfully", "data": prediction_result},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def list(self, request):
        """Override list method to filter predictions by user
        """
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        
        # Fetch params
        ticker = request.query_params.get('ticker', None)
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        if ticker:
            queryset = queryset.filter(stock_symbol=ticker)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
          
        serializer = self.get_serializer(queryset, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
# Viewset for Telegram Users
class TelegramUserViewSet(viewsets.ModelViewSet):
    """Viewset for managing Telegram users
    """
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAuthenticated]
    
class HealthCheckView(generics.GenericAPIView):
    """Health check endpoint to verify API is running
    """
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)