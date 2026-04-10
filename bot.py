# bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import db

# Отключаем логирование HTTP-запросов от httpx
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_data = {}

QUESTIONS = [
    ("Что вам больше нравится?", [("Работа с людьми","people"),("Данные / аналитика","data"),("Техника / механизмы","tech"),("Творчество","creative")]),
    ("Какой формат работы предпочитаете?", [("В офисе","office"),("Удалённо","remote"),("В разъездах","travel")]),
    ("Насколько важна для вас зарплата?", [("Очень важна","high_salary"),("Средне","medium_salary"),("Не главное","low_salary")]),
    ("Готовы ли учиться новому?", [("Да, постоянно","learning_yes"),("Только в знакомой сфере","learning_familiar"),("Нет, не готов","learning_no")]),
    ("Какой тип задач вам ближе?", [("Анализировать","analytical"),("Мастерить руками","practical"),("Общаться","communicative"),("Придумывать","creative_tasks")])
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Начать опрос", callback_data="start_quiz")],
                [InlineKeyboardButton("О проекте", callback_data="about")]]
    await update.message.reply_text("Привет! Я помогу найти профессию.\nНажми 'Начать опрос'", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "start_quiz":
        user_data[user_id] = {"answers": []}
        await query.edit_message_text("Давай начнём!")
        await ask_question(query.message, 0)
    elif data == "about":
        await query.edit_message_text("Career Helper Bot\nКороткий опрос → подбор профессий из базы.")
    elif data.startswith("answer_"):
        parts = data.split("_", 2)
        if len(parts) != 3:
            await query.edit_message_text("Ошибка формата. Начните заново /start")
            return
        _, step_str, tag = parts
        step = int(step_str)
        user_data[user_id]["answers"].append(tag)
        if step + 1 < len(QUESTIONS):
            await ask_question(query.message, step + 1)
            await query.delete_message()
        else:
            await query.delete_message()
            await show_results(user_id, context.bot)

async def ask_question(message, step: int):
    text, options = QUESTIONS[step]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"answer_{step}_{tag}")] for opt, tag in options]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_results(user_id: int, bot):
    answers = user_data[user_id]["answers"]
    professions = db.find_professions_by_tags(answers)
    if not professions:
        text = "Совпадений не найдено. Попробуйте /start заново."
    else:
        text = "Вам подходит:\n\n" + "\n\n".join(f"{p['name']}\n{p['description']}" for p in professions[:3]) + "\n\n/start для повтора"
    await bot.send_message(chat_id=user_id, text=text)
    del user_data[user_id]

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Используйте /start")

def main():
    db.init_db()
    db.add_sample_professions()
    app = Application.builder().token("8146890312:AAFcpfNI4TXP3w1QGU_JJqTc9lyxI4IbJkw").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    logger.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()