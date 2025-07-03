from rest_framework import serializers
from .models import StockPrediction, TelegramUser
from django.contrib.auth.models import User
        
        
class StockPredictionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = StockPrediction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'mse', 'rmse', 'r2', 'plot_urls', 'metrics_json')
        
        
class TelegramUserSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = TelegramUser
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'telegram_user_id', 'chat_id')
        
class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)
        
      
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)  