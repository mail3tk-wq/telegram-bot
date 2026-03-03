import os
import hashlib
import hmac
import requests
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from threading import Thread
import uuid
# ====== ENV ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MERCHANT_ACCOUNT = os.getenv("MERCHANT_ACCOUNT")
MERCHANT_SECRET = os.getenv("MERCHANT_SECRET")
DOMAIN_NAME = os.getenv("DOMAIN_NAME")
print("BOT_TOKEN =", BOT_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

PRICE = 99
CURRENCY = "UAH"

# ====== CREATE PAYMENT ======
def create_payment(user_id):

    order_reference = f"{user_id}_{uuid.uuid4().hex}"
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
    )

    print("WAYFORPAY RESPONSE:", response.text)

    data = response.json()

    return data.get("invoiceUrl")
# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    payment_url = create_payment(user_id)

    if not payment_url:
        bot.send_message(message.chat.id, "Помилка створення платежу 😢")
        return

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "💳 Придбати за 99 грн",
            url=payment_url
        )
    )

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

    data = request.get_json(force=True, silent=True)

    if not data:
        data = request.form.to_dict()

    print("WAYFORPAY DATA:", data)

    order_reference = data.get("orderReference")
    user_id = int(order_reference.split("_")[0])

        link = bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1
        )

        bot.send_message(
            user_id,
            f"Оплату підтверджено ✅\n\nОсь ваше одноразове посилання:\n{link.invite_link}"
        )

    return "OK", 200
# ====== TELEGRAM WEBHOOK ======
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


# ====== RUN SERVER ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)








