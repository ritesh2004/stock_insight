import logging

from telegram import ForceReply, Update, InputFile, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from django.core.management.base import BaseCommand

from decouple import config

from asgiref.sync import sync_to_async

# Load DB Models
from api.models import TelegramUser, StockPrediction
from django.contrib.auth.models import User

# ML models utility functions
from ml_model.predict_utils import fetch_ohlcv_data, predict_with_plot

# Subscription handler
import stripe

# Set up Stripe
stripe.api_key = config("STRIPE_SECRET_KEY")

BOT_TOKEN = config("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Global User Variable
global_user = None

# User create
@sync_to_async
def get_or_create_user(chat):
    user, created = User.objects.get_or_create(username=chat.id)
    return user

@sync_to_async
def get_or_create_telegram_user(user, chat_id, username):
    tg_user, created = TelegramUser.objects.get_or_create(
        chat_id=chat_id,
        defaults={'username': username, 'user': user}
    )
    return tg_user, created

@sync_to_async
def get_prediction(ticker, chat):
    """Fetch stock prediction for a given ticker."""
    try:
        df = fetch_ohlcv_data(ticker)
        if df.empty:
            return None, "No data found for the ticker."
        prediction = predict_with_plot(df, ticker)
        if prediction is None:
            return None, "Prediction failed."
        # Save the prediction to the database
        stock_prediction = StockPrediction.objects.create(
            stock_symbol=ticker,
            user=User.objects.filter(username = chat.id).first(),  
            next_day_price=prediction['next_day_price'],
            metrics_json=prediction['metrics'],
            plot_urls=prediction['plot_urls']
        )
        print(stock_prediction)
        return stock_prediction, None
    except Exception as e:
        logger.error(f"Error fetching prediction for {ticker}: {e}")
        return None, str(e)
    
@sync_to_async
def get_latest_predictions(chat):
    """Fetch the latest stock predictions."""
    user = User.objects.filter(username=chat.id).first()
    if not user:
        logger.warning(f"No user found for chat_id: {chat.id}")
        return list(StockPrediction.objects.none())
    
    return list(StockPrediction.objects.filter(user = user).order_by('-created_at')[:5])

@sync_to_async
def rate_limiter(user, chat_id, username, message):
    """Rate limiting logic to restrict daily requests."""
    telegram_user, created = TelegramUser.objects.get_or_create(
        chat_id=chat_id,
        defaults={'username': username, 'user': user}
    )
    # Increment daily request count
    if telegram_user.last_request_date != message.date.date():
        telegram_user.daily_request_count = 0
        telegram_user.last_request_date = message.date.date()
    
    if telegram_user.daily_request_count >= 5 and not telegram_user.is_pro:
        return None
        
    # Update last request date
    telegram_user.daily_request_count += 1
    telegram_user.save()
    return telegram_user.daily_request_count

@sync_to_async
def get_checkout_session(chat):
    """Create a Stripe checkout session for subscription."""
    create_checkout_session(request={"user":chat})

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    chat = update.effective_chat
    
    loggedin_user = await get_or_create_user(chat)
    telegram_user, created = await get_or_create_telegram_user(loggedin_user, chat.id, user.username)
    global global_user 
    global_user = telegram_user  # Store the Telegram user globally for later use
    
    if created:
        logger.info(f"New Telegram user created: {telegram_user.username} ({telegram_user.chat_id})")
    else:
        logger.info(f"Existing Telegram user found: {telegram_user.username} ({telegram_user.chat_id})")
        
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm your Stock Insight Bot.\n"
        f"You are in {telegram_user.is_pro and 'Premium' or 'Free'} mode.\n"
        "Use /help to see available commands.",
        reply_markup=ForceReply(selective=True),
    )
    
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle stock prediction requests."""
    if context.args:
        chat = update.effective_chat
        ticker = context.args[0].upper()
        # Implemeting Rate Limiting Logic
        
        status = await rate_limiter(user=update.effective_user, chat_id=chat.id, username=update.effective_user.username, message=update.message)
        
        if status is None:
            await update.message.reply_text(
                "You have reached your daily limit of 5 predictions. Please try again tomorrow.\n"
                "Or /subscribe to get unlimited access."
            )
            return
        
        # Here you would implement the logic to fetch and return stock predictions
        await update.message.reply_text(
            f"Fetching prediction for ticker: {ticker}...\n"
            "This feature is under development."
        )
        stock_prediction, error = await get_prediction(ticker, chat)
        
        await update.message.reply_text(f"Prediction for {ticker}:\n"
            f"Next Day Price: {round(stock_prediction.next_day_price, 2) if stock_prediction else 'N/A'}\n"
            f"Plot URLs: {', '.join(stock_prediction.plot_urls) if stock_prediction else 'N/A'}\n"
        )
        photos = [
            InputMediaPhoto(media=open(url, 'rb'))
            for url in stock_prediction.plot_urls
        ]
        await update.message.reply_media_group(
            media=photos,
        )
    else:
        await update.message.reply_text(
            "Please provide a stock ticker symbol. Usage: /predict TICKER"
        )
        
async def latest_predictions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display the latest stock predictions."""
    chat = update.effective_chat
    predictions = await get_latest_predictions(chat=chat)
    if predictions:
        response = "Latest Stock Predictions:\n"
        for prediction in predictions:
            response += (
                f"Ticker: {prediction.stock_symbol}, "
                f"Next Day Price: {round(prediction.next_day_price, 2)}, "
                f"Created At: {prediction.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("No predictions found.")
        
async def subscription_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle subscription requests."""
    chat = update.effective_chat
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
        success_url='https://t.me/django_ritesh_bot',
        cancel_url='https://t.me/django_ritesh_bot',
        metadata={
            'chat_id': chat.id,
        },
    )
    await update.message.reply_html(
        "🔗 <b>Subscribe to Premium</b>\n\n"
        "Click the link below to complete your subscription:\n"
        f"<a href='{checkout_session.url}'>💳 Pay Now - ₹199/month</a>\n\n"
        "✅ After payment, return to this bot\n"
        "💬 Use /start to check your premium status",
        disable_web_page_preview=True
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_html(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/predict TICKER - Get stock prediction for a ticker\n"
        "/latest - Get latest stock predictions\n"
        "Send any text message to echo it back.",
        reply_markup=ForceReply(selective=True),
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(str(BOT_TOKEN)).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("predict", predict))
    application.add_handler(CommandHandler("latest", latest_predictions))
    application.add_handler(CommandHandler("subscribe", subscription_handler))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


class Command(BaseCommand):
    help = "Start the Telegram bot"
    def handle(self, *args, **options):
        """Handle the command to start the Telegram bot."""
        logger.info("Starting Telegram bot...")
        main()
        logger.info("Telegram bot stopped.")