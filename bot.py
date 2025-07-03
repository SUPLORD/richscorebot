import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["💰 Деньги", "🏠 Квартира"], ["🚘 Машина", "✈️ Путешествие"], ["💼 Бизнес", "📱 Айфон"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Это RICHSCORE 💸\n\n"
        "Выбери свою цель, а я помогу рассчитать путь 👇",
        reply_markup=reply_markup
    )

# Обработка выбранной цели
async def handle_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text
    await update.message.reply_text(f"🔥 Цель принята: {goal}\n\n💬 Сколько ты готов откладывать в месяц?")

# Запуск приложения
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal))

print("🚀 БОТ ЗАПУСКАЕТСЯ... RICHSCORE ждёт тебя.")
app.run_polling()
