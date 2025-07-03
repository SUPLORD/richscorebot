import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

# Этапы сценария
(NAME, GOAL, DREAM, AMOUNT, MONTHLY, PERSONALITY, SHOW_PLAN) = range(7)
user_data = {}

# Приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Привет! Я RICHSCORE — твой финансовый друг, ментор, и немного психотерапевт денег.\n"
        "Обещаю: никакого занудства, только работающие фишки.\n\n"
        "Как к тебе обращаться? (Имя, ник, супергерой — всё честно!)"
    )
    return NAME

# Имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    context.user_data["name"] = name
    await update.message.reply_text(
        f"Привет, {name}! 👋\n\n"
        "Теперь выбери цель или мечту (можешь написать свою):",
        reply_markup=ReplyKeyboardMarkup(
            [["💼 Бизнес", "🏠 Квартира", "🚘 Машина"],
             ["📱 Айфон", "🌴 Путешествие", "💰 Свобода"],
             ["✍️ Своя цель"]],
            one_time_keyboard=True, resize_keyboard=True)
    )
    return GOAL

# Цель или мечта
async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text
    context.user_data["goal"] = goal
    if goal == "✍️ Своя цель":
        await update.message.reply_text(
            "Тогда напиши свой вариант — без фильтра, как чувствуешь:"
        )
        return DREAM
    await update.message.reply_text(
        f"Вау, {goal} — мощно!\n\n"
        "Теперь скажи, сколько денег тебе на это нужно (только цифры, без ₽):",
        reply_markup=ReplyKeyboardRemove()
    )
    return AMOUNT

async def get_dream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dream = update.message.text
    context.user_data["goal"] = dream
    await update.message.reply_text(
        f"Супер, цель записал: {dream}\n\n"
        "Теперь сумма на мечту (только цифры, без ₽):"
    )
    return AMOUNT

# Сумма
async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.replace(" ", ""))
        context.user_data["amount"] = amount
        await update.message.reply_text(
            f"Окей, {amount:,} ₽ — вызов принят.\n\n"
            "А сколько ты реально можешь откладывать каждый месяц?"
        )
        return MONTHLY
    except Exception:
        await update.message.reply_text("Только цифры, без лишнего. Пробуй ещё раз:")
        return AMOUNT

# Месячный взнос
async def get_monthly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        monthly = int(update.message.text.replace(" ", ""))
        context.user_data["monthly"] = monthly
        await update.message.reply_text(
            "Честно, насколько ты готов рисковать? (Ответь: \"Минимум\", \"Средне\", \"Максимум\")"
        )
        return PERSONALITY
    except Exception:
        await update.message.reply_text("Цифрами, плиз! Сколько в месяц можешь откладывать?")
        return MONTHLY

# Риск-профиль
async def get_personality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    risk = update.message.text.strip().lower()
    context.user_data["risk"] = risk
    name = context.user_data["name"]
    goal = context.user_data["goal"]
    amount = context.user_data["amount"]
    monthly = context.user_data["monthly"]
    risk_map = {
        "минимум": 0.06,
        "средне": 0.12,
        "максимум": 0.18
    }
    rate = risk_map.get(risk, 0.10)
    months = 0
    capital = 0
    while capital < amount and months < 1000:
        capital = capital * (1 + rate/12) + monthly
        months += 1
    years = months // 12
    rest_months = months % 12

    personality_tip = {
        "минимум": "Ты — спокойный инвестор, но иногда нужно и немного авантюризма!",
        "средне": "Баланс — твоё второе имя! Ты знаешь, когда идти вперёд.",
        "максимум": "Вах! Ты — волк Уолл-стрит! Но не забывай про риски и сон 😏"
    }.get(risk, "Ты уникальный финансист, как тебе удобнее — так и делай!")

    await update.message.reply_text(
        f"🧠 {personality_tip}\n\n"
        f"🎯 Цель: {goal}\n"
        f"💰 Сумма: {amount:,} ₽\n"
        f"💵 Откладываешь: {monthly:,} ₽/мес\n"
        f"🚦 Риск: {risk.capitalize()}\n"
        f"⏳ Примерный срок: {years} лет и {rest_months} месяцев\n"
        f"🤖 Совет RICHSCORE: хочешь ускориться — увеличивай ежемесячный вклад или цель разбей на этапы.\n\n"
        "Напиши /start, чтобы сделать новый расклад! Или /pro для подключения платных функций (PDF, стратегия, поддержка).\n"
    )
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён. Я рядом, когда захочешь — напиши /start 😉")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
        DREAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dream)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
        MONTHLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_monthly)],
        PERSONALITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_personality)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv)
print("🚀 БОТ ЗАПУСКАЕТСЯ... RICHSCORE жжёт рынок.")
app.run_polling()
