import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Этапы диалога
(
    CHOOSING_NAME,
    CHOOSING_GOAL,
    ASK_AMOUNT,
    ASK_PAYMENT,
    SHOW_RESULT,
) = range(5)

# Список целей
GOALS = [
    "💼 Бизнес",
    "🏠 Квартира",
    "🚘 Машина",
    "🌴 Путешествие",
    "📱 Айфон",
    "💻 Компьютер",
    "💰 Подушка безопасности",
]

# Хранилище данных
user_data = {}

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я RICHSCORE, твой личный финансовый бот 💸\n\nКак тебя зовут?"
    )
    return CHOOSING_NAME

# Имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["name"] = update.message.text
    keyboard = [[g] for g in GOALS]
    await update.message.reply_text(
        f"Отлично, {user_data['name']}!\n\nТеперь выбери цель:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return CHOOSING_GOAL

# Цель
async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["goal"] = update.message.text
    await update.message.reply_text("Сколько стоит твоя цель? (в рублях, только число)")
    return ASK_AMOUNT

# Сумма цели
async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_data["amount"] = int(update.message.text.replace(" ", ""))
        await update.message.reply_text("Сколько ты можешь откладывать в месяц? (в рублях)")
        return ASK_PAYMENT
    except ValueError:
        await update.message.reply_text("Введи только число, без лишних символов.")
        return ASK_AMOUNT

# Ежемесячный взнос и расчёт
async def get_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        payment = int(update.message.text.replace(" ", ""))
        user_data["payment"] = payment

        goal = user_data["goal"]
        amount = user_data["amount"]
        rate = 0.15  # Доходность 15%
        months = 0
        total = 0

        while total < amount and months < 1000:
            total = total * (1 + rate / 12) + payment
            months += 1

        years = months // 12
        rest_months = months % 12

        text = f"""📊 *ТВОЙ РАСКЛАД*

🎯 Цель: {goal}
💰 Сумма: {amount:,} ₽
📦 Взнос: {payment:,} ₽ / мес
📈 Доходность: 15% годовых

⏳ Примерный срок: {years} лет и {rest_months} мес

⚠️ Это не финсовет, а дружеский расчёт.
Я не ЦБ, но стараюсь быть честным 😉
"""
        await update.message.reply_markdown(text)
        await update.message.reply_text("Напиши /start — чтобы рассчитать новую цель.")
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("Введи только число, без лишнего.")
        return ASK_PAYMENT

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей! Если передумаешь — напиши /start.")
    return ConversationHandler.END

# Основной запуск
if __name__ == "__main__":
    print("🚀 БОТ ЗАПУСКАЕТСЯ... RICHSCORE ждёт тебя.")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CHOOSING_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
            ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            ASK_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()
