# 📈 Stock Insight – Django Stock Price Predictor

A production-ready Django application that predicts the next-day closing price of a stock using an LSTM model, with Stripe-powered premium plans, Telegram bot integration, and full Docker support.

---

## 🎥 Full Functional Demo Video

https://github.com/user-attachments/assets/87ab728e-8b5d-4837-bb4e-a915160c2948

---

## 🚀 Features

* 📊 Predict next-day stock prices using pre-trained LSTM model
* 📦 REST API + Django views with Tailwind templates
* 📂 Media files served via Nginx
* 💰 Stripe Checkout integration (Free: 5 req/day, Pro: unlimited)
* 🤖 Telegram Bot commands (`/start`, `/predict`, `/latest`, `/help`, `/subscribe`)
* 🐳 Fully Dockerized with Gunicorn & Nginx
* ✅ Production-ready with `DEBUG=False`, healthcheck, and CSRF security
* 📈 Logs prediction metrics and charts

---

## 🧱 Tech Stack

* Backend: Django + Django REST Framework
* ML: TensorFlow (LSTM model)
* Auth: Django sessions + JWT
* Billing: Stripe Checkout + Webhooks
* Bot: Python Telegram Bot v22.1
* Frontend: Django Templates + Tailwind CSS
* Deployment: Docker + Gunicorn + Nginx
* DevOps: Docker Compose

---

## 🐳 Local Development (Docker)

### 1. Clone the repo

```bash
git clone https://github.com/ritesh2004/stock_insight.git
cd stock-insight
```

### 2. Set up environment variables

Create `.env` file from example:

```bash
cp .env
```

Copy all Keys from .env.example and Paste into .env file. Then fill values for corresponding keys in .env file.

---

### 3. Build & start containers

```bash
docker-compose up --build
```

* App: [http://localhost](http://localhost)
* Healthcheck: [http://localhost/healthz/](http://localhost/healthz/)
* Media: `/media/`

---

## 🔐 Stripe Integration

### Download Stripe CLI for your System

#### Follow this link - [https://docs.stripe.com/stripe-cli#install](https://docs.stripe.com/stripe-cli#install)

### Start local webhook tunnel:

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe/
```

Copy the webhook secret and add it to `.env` as:

```env
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

Trigger test events:

```bash
stripe trigger checkout.session.completed
```

---

## 🤖 Telegram Bot

Run the bot (already in Docker as `telegram_bot`):

* `/start`: links Telegram user
* `/predict TSLA`: fetch prediction & send charts
* `/latest`: send last prediction
* `/help`: show usage
* `/subscribe`: subscribe for premium plan

---

## 🛠 Management Commands

```bash
# Run a prediction manually
python manage.py predict --ticker TSLA

# Predict for all previously used tickers
python manage.py predict --all

# Run Telegram Bot
python manage.py telegrambot
```

---

## 📁 Folder Structure

```
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .env.example
├── manage.py
├── media/                ← Store generated charts
├── stock_insight/        ← Django settings
├── core/                 ← Views, forms, templates
├── api/                  ← Models, APIs logic
├── ml_model              ← ML model logics
```

---

## 🔒 API Structure

| Method | Endpoint                | Auth Required  | Description                                        |
| ------ | ----------------------- | -------------  | -------------------------------------------------- |
| POST   | `/api/v1/register/`     | ❌ No          | Register New Users                                 |
| POST   | `/api/v1/token/`        | 🟨 Basic       | Return JWT accessToken and refreshToken            |
| POST   | `/api/v1/predict/`      | ✅ Yes         | Accept `ticker` and return `{next_day_price, mse, rmse, r2, plot_urls[]}`|
| GET    | `/api/v1/predictions/`  | ✅ Yes         | Return Stored Predictions                          |
| GET    | `/healthz/`             | ❌ No          | Return server status                               |

## ✅ Health Check

Nginx and Docker Compose will check:

```
GET /healthz/
→ 200 OK
```

---

## 📦 Media Files

| Type   | Served By  | Path       |
| ------ | ---------- | ---------- |
| Media  | Nginx      | `/media/`  |

---

## ⚠️ Security Notes

* `DEBUG=False` in production
* Use `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, and `SECURE_SSL_REDIRECT=True`

---

## 📞 Contacts

* LinkedIn: [Ritesh Pramanik](https://www.linkedin.com/in/ritesh-pramanik-8ba316260)
* Email: [ritesh.work.2004@gmail.com](mailto:ritesh.work.2004@gmail.com)
* Facebook: [Ritesh Pramanik](https://www.facebook.com/itzriteshpramanik)
* Instagram: [@__ritesh.dev](https://www.instagram.com/__ritesh.dev/)

---

## 📜 License

MIT License – Free to use and modify.
