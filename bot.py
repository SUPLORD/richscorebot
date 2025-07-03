import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я RICHSCORE. Помогу тебе с финансами. Напиши /цель")

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отлично! Напиши свою цель, например: Купить квартиру за 10 000 000 ₽")

def main():
    print("🚀 БОТ ЗАПУСКАЕТСЯ... RICHSCORE ждёт тебя.")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("цель", goal))

    app.run_polling()

if __name__ == "__main__":
    main()
