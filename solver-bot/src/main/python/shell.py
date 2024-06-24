import json

from logger import logger
from solution import calc_solution
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

PY_DIR = "solver-bot/src/main/python/"

CONFIG = json.load(open(
    PY_DIR + "config/config.json", "r"))

ORDER, EQUATION, INITIAL_X, INITIAL_Y, REACH_POINT, STEP_SIZE = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(PY_DIR + "assets/texts/START.txt", "r", encoding="utf-8") as file:
        file_text = file.read()
    await update.message.reply_text(file_text)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(PY_DIR + "assets/texts/HELP.txt", "r", encoding="utf-8") as file:
        file_text = file.read()
    await update.message.reply_text(file_text)


async def solve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["First", "Second"]]

    await update.message.reply_text(
        "Choose the order of the differential equation to be solved.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        ),
    )

    return ORDER


async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Order of %s: %s", user.id, update.message.text)
    context.user_data['order'] = update.message.text

    if context.user_data['order'] == "First":
        await update.message.reply_text(
            "Enter the differential equation like: y' = f(x, y).",
            reply_markup=ReplyKeyboardRemove()
        )
    elif context.user_data['order'] == "Second":
        await update.message.reply_text(
            "Enter the differential equation like: y'' = f(x, y, z = y').",
            reply_markup=ReplyKeyboardRemove()
        )

    return EQUATION


async def equation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Equation of %s: %s", user.id, update.message.text)
    context.user_data['equation'] = update.message.text
    await update.message.reply_text("Enter the initial state of x.")

    return INITIAL_X


async def initial_x(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Initial x of %s: %s", user.id, update.message.text)
    context.user_data['initial_x'] = update.message.text

    if context.user_data['order'] == "First":
        await update.message.reply_text(
            "Enter the initial state of y."
        )
        return INITIAL_Y
    elif context.user_data['order'] == "Second":
        await update.message.reply_text(
            "Enter the initial state of y and y' separated by space."
        )

    return INITIAL_Y


async def initial_y(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Initial y of %s: %s", user.id, update.message.text)
    context.user_data['initial_y'] = update.message.text
    await update.message.reply_text("Enter the point of approach.")

    return REACH_POINT


async def reach_point(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Reach point of %s: %s", user.id, update.message.text)
    context.user_data['reach_point'] = update.message.text
    await update.message.reply_text("Enter the step dimension.")

    return STEP_SIZE


async def step_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("Step size of %s: %s", user.id, update.message.text)
    context.user_data['step_size'] = update.message.text
    await calc_solution(update, context)
    context.user_data.clear()

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s canceled solving.", user.id)
    context.user_data.clear()
    await update.message.reply_text(
        "Actions canceled.",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(CONFIG['TELEGRAM_TOKEN']).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("solve", solve)],
        states={
            ORDER:
            [MessageHandler(filters.Regex("^(First|Second)$"), order)],
            EQUATION:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, equation)],
            INITIAL_X:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, initial_x)],
            INITIAL_Y:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, initial_y)],
            REACH_POINT:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, reach_point)],
            STEP_SIZE:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, step_size)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("solve", solve))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
