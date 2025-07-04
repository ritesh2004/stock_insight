from django.core.management.base import BaseCommand
from django.conf import settings
from ml_model.predict_utils import predict_with_plot, fetch_ohlcv_data
from api.models import StockPrediction
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Predict stock prices'
    def bold_text(self, text):
        """Helper method to make text bold using ANSI codes"""
        return f"\033[1m{text}\033[0m"
    
    def add_arguments(self, parser):
        parser.add_argument('--ticker', type=str, help='Stock ticker symbol')
        parser.add_argument('--all', action='store_true', help='Predict for all stocks in the database')
    
    def handle(self, *args, **kwargs):
        # Import the predict function from the telegrambot module
        tickers = []
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR("No superuser found. Please create a superuser first."))
            return
        
        if kwargs['ticker']:
            tickers = [kwargs['ticker'].upper()]
            
            df = fetch_ohlcv_data(tickers[0])
            if df is None:
                self.stdout.write(self.style.ERROR(f"Failed to fetch data for ticker: {tickers[0]}"))
                return
            prediction = predict_with_plot(df, tickers[0])
            
            if prediction:
                StockPrediction.objects.create(
                    stock_symbol=tickers[0],
                    user = admin_user,
                    next_day_price=prediction['next_day_price'],
                    metrics_json=prediction['metrics'],
                    plot_urls=prediction['plot_urls']
                )
                self.stdout.write(self.style.SUCCESS(f"Prediction completed for {tickers[0]}"))
                self.stdout.write(self.bold_text(f"Next day price prediction: {prediction['next_day_price']}"))
            else:
                self.stdout.write(self.style.ERROR(f"Prediction failed for {tickers[0]}"))
            
        elif kwargs['all']:
            all_predictions = StockPrediction.objects.filter(user=admin_user)
            
            for prediction in all_predictions:
                self.stdout.write(self.bold_text(f"Stock: {prediction.stock_symbol}, Next Day Prediction: {prediction.next_day_price}"))
                
        else:
            self.stdout.write(self.style.ERROR("Please provide a ticker symbol or use --all to predict for all stocks."))