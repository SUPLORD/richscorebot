from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from reportlab.pdfgen import canvas

# Этапы разговора
CHOOSING_GOAL, ASK_REASON, ASK_AMOUNT, ASK_MONTHLY = range(4)

# Память
user_data = {}

# Список целей
GOALS = ["📱 Айфон", "🚗 Машина", "🏠 Квартира", "🏢 Пентхаус", "🌴 Путешествие", "💼 Собственный бизнес"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я RICHSCORE. Я не брокер и не ЦБ — я честный финансовый собеседник.\n\n"
        "Давай разложим твою мечту по полочкам. Выбери цель:",
        reply_markup=ReplyKeyboardMarkup([GOALS], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHOOSING_GOAL

async def choose_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    goal = update.message.text
    user_data[update.effective_user.id] = {"goal": goal}
    await update.message.reply_text(
        f"Хороший выбор — {goal}.\nТы хочешь это ради кайфа или по необходимости?"
    )
    return ASK_REASON

async def ask_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reason = update.message.text
    user_data[update.effective_user.id]["reason"] = reason
    await update.message.reply_text("Сколько тебе нужно на это в рублях?")
    return ASK_AMOUNT

async def ask_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(" ", ""))
    except:
        await update.message.reply_text("Напиши сумму числом. Например: 500000")
        return ASK_AMOUNT
    user_data[update.effective_user.id]["amount"] = amount
    await update.message.reply_text("Сколько ты можешь откладывать в месяц?")
    return ASK_MONTHLY

async def ask_monthly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        monthly = float(update.message.text.replace(" ", ""))
    except:
        await update.message.reply_text("Пожалуйста, напиши число. Например: 10000")
        return ASK_MONTHLY

    data = user_data[update.effective_user.id]
    data["monthly"] = monthly
    r = 0.01  # 12% годовых / 12 месяцев
    amount, pmt = data["amount"], data["monthly"]

    # Расчёт срока (в месяцах)
    if pmt <= 0 or r <= 0:
        months = 999
    else:
        from math import log, ceil
        months = ceil(log((pmt + r * 0) / (pmt + r * 0 - r * amount)) / log(1 + r))

    years = months // 12
    months_left = months % 12

    data["years"], data["months_left"] = years, months_left

    # Генерация PDF
    filename = f"richscore_{update.effective_user.id}.pdf"
    c = canvas.Canvas(filename)
    c.setFont("Helvetica", 14)
    c.drawString(100, 800, f"🎯 Цель: {data['goal']}")
    c.drawString(100, 780, f"💭 Причина: {data['reason']}")
    c.drawString(100, 760, f"💰 Сумма: {amount:,.0f} ₽")
    c.drawString(100, 740, f"📦 Откладываем в месяц: {pmt:,.0f} ₽")
    c.drawString(100, 720, f"📈 Доходность: 12% годовых")
    c.drawString(100, 700, f"⏳ Срок: {years} лет и {months_left} месяцев")
    c.drawString(100, 660, "⚠️ Это не финансовый совет, а дружеский расчёт.")
    c.drawString(100, 640, "Я не ЦБ, но стараюсь быть честным 🤝")
    c.save()

    # Отправка PDF
    await update.message.reply_document(open(filename, "rb"), filename="Твой_расклад_RICHSCORE.pdf")

    await update.message.reply_text("Если хочешь попробовать другую цель — набери /start.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, расклад отменён.")
    return ConversationHandler.END

app = ApplicationBuilder().token("7572906236:AAE7kinfyi_1oIA6Kg4MpYNONBniqIATffc").build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_goal)],
        ASK_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_reason)],
        ASK_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_amount)],
        ASK_MONTHLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_monthly)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(conv)

print("▶️ БОТ ЗАПУЩЕН... RICHSCORE ждёт тебя.")
app.run_polling()
