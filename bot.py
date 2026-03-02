import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8759700488:AAHdk8UgVnCd8z1fWQa14PoBpR8fQtpHaiU"
bot = telebot.TeleBot(TOKEN)

PAYMENT_LINK = "https://secure.wayforpay.com/button/b0694b5220480"

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    buy_button = InlineKeyboardButton("💳 Придбати за 99", url=PAYMENT_LINK)
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

print("Бот запущений ✅")
bot.polling(none_stop=True)