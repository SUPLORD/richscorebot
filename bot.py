import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# 📌 Получаем токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🚀 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я RICHSCORE. Готов к раскладу? 💸")

# 🎯 Пример команды /цель
async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠 Сейчас добавим твою цель...")

# ⚙️ Настройка бота
def main():
    print("🚀 БОТ ЗАПУСКАЕТСЯ... RICHSCORE ждёт тебя.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("цель", goal))

    app.run_polling()

if __name__ == "__main__":
    main()
