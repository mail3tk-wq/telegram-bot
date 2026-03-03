import os
import hashlib
import hmac
import requests
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread
from datetime import datetime

# ====== ENV ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MERCHANT_ACCOUNT = os.getenv("MERCHANT_ACCOUNT")
MERCHANT_SECRET = os.getenv("MERCHANT_SECRET")
DOMAIN_NAME = os.getenv("DOMAIN_NAME")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

PRICE = 99
CURRENCY = "UAH"

# ====== CREATE PAYMENT ======
def create_payment(user_id):

    order_reference = str(user_id)
    order_date = str(int(datetime.now().timestamp()))

    sign_string = ";".join([
        MERCHANT_ACCOUNT,
        DOMAIN_NAME,
        order_reference,
        order_date,
        str(PRICE),
        CURRENCY,
        "Girls Room Access",
        "1",
        str(PRICE)
    ])

    merchant_signature = hmac.new(
        MERCHANT_SECRET.encode(),
        sign_string.encode(),
        hashlib.md5
    ).hexdigest()

    payload = {
        "transactionType": "CREATE_INVOICE",
        "merchantAccount": MERCHANT_ACCOUNT,
        "merchantDomainName": DOMAIN_NAME,
        "merchantSignature": merchant_signature,
        "apiVersion": 1,
        "orderReference": order_reference,
        "orderDate": int(order_date),
        "amount": PRICE,
        "currency": CURRENCY,
        "productName": ["Girls Room Access"],
        "productCount": [1],
        "productPrice": [PRICE]
    }

    response = requests.post(
        "https://api.wayforpay.com/api",
        json=payload
    ).json()

    return response.get("invoiceUrl")


# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    buy_button = InlineKeyboardButton("💳 Придбати за 99 грн", url="https://example.com")
    markup.add(buy_button)

    bot.send_message(
        message.chat.id,
        """🩷 Вітаю у Girls Room

Твій особистий простір, де стиль стає легкою звичкою, а образ — продуманим до дрібниць ✨

Що всередині:
 • секрети гардеробу, які реально працюють
 • маленькі трюки для щоденного образу
 • фінальний чек-лист + персональна пропозиція на жакет бренду 💎

🫰Готова відкрити першу кімнату? Натискай нижче та почни свою стильну трансформацію зараз!""",
        reply_markup=markup
    )


# ====== WEBHOOK ======
@app.route("/wayforpay", methods=["POST"])
def wayforpay_webhook():

    data = request.json

    if data.get("transactionStatus") == "Approved":

        user_id = int(data.get("orderReference"))

        link = bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1
        )

        bot.send_message(
            user_id,
            f"Оплату підтверджено ✅\n\nОсь ваше одноразове посилання:\n{link.invite_link}"
        )

    return "OK", 200


# ====== RUN ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

