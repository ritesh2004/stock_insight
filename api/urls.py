from django.urls import path, include
from .views import RegisterUserView, StockPredictionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('predict/', StockPredictionViewSet.as_view({'post': 'create'}), name='stock_prediction_create'),
    path('predictions/', StockPredictionViewSet.as_view({ 'get' : 'list' }), name='stock_prediction_list'),
]