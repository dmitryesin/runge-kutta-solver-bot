import json
import psycopg2

from logger import logger
from plotting.plotter import plot_solution
from solution import (
    get_result_info,
    get_x_values,
    get_y_values,
    get_solution)
from equation.equation_parser import format_equation
from equation.equation_validator import (
    validate_symbols,
    validate_parentheses)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

psql = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)

PY_DIR = "solver-bot/src/main/python/"

CONFIG = json.load(open(
    PY_DIR + "config/config.json", "r", encoding="utf-8"))

LANG_TEXTS = json.load(open(
    PY_DIR + "languages.json", "r", encoding="utf-8"))

MENU, EQUATION, INITIAL_X, INITIAL_Y, REACH_POINT, STEP_SIZE = range(6)

DEFAULT_METHOD = "method_runge_kutta"
DEFAULT_ROUNDING = "4"
DEFAULT_LANGUAGE = "en"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message:
        return MENU

    user_settings = await get_user_settings_from_psql(update.effective_user.id)
    context.user_data['method'] = user_settings.get('method', DEFAULT_METHOD)
    context.user_data['rounding'] = user_settings.get('rounding', DEFAULT_ROUNDING)
    context.user_data['language'] = user_settings.get('language', DEFAULT_LANGUAGE)

    await save_user_settings_to_psql(update.effective_user.id, context.user_data)

    current_state = context.user_data.get("state", None)
    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    if current_state in [EQUATION, INITIAL_X, INITIAL_Y, REACH_POINT, STEP_SIZE]:
        user = update.message.from_user
        logger.info("User %s canceled solving.", user.id)

        await save_user_settings(context)

    keyboard = [
        [
            InlineKeyboardButton(
                LANG_TEXTS[current_language]["solve"],
                callback_data="solve"),
            InlineKeyboardButton(
                LANG_TEXTS[current_language]["settings"],
                callback_data="settings")
        ],
        [
            InlineKeyboardButton(
                LANG_TEXTS[current_language]["solve_history"],
                callback_data="solve_history")
        ]
    ]

    with open(PY_DIR + "assets/texts/START_EN.txt", "r", encoding="utf-8") as file:
        start_en = file.read()

    with open(PY_DIR + "assets/texts/START_RU.txt", "r", encoding="utf-8") as file:
        start_ru = file.read()

    if update.message:
        await update.message.reply_text(
            start_en if current_language == "en" else start_ru,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        query = update.callback_query
        await query.answer()
        if query.message and query.message.text:
            await query.edit_message_text(
                start_en if current_language == "en" else start_ru,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        else:
            await query.message.reply_text(
                start_en if current_language == "en" else start_ru,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )

    return MENU


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    keyboard = [
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["change_method"],
            callback_data="settings_method")],
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["change_rounding"],
            callback_data="settings_rounding")],
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["change_language"],
            callback_data="settings_language")],
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["back"],
            callback_data="back")]
    ]

    await query.edit_message_text(
        LANG_TEXTS[current_language]["settings_menu"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return MENU


async def method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_method = query.data
    context.user_data['method'] = current_method

    await save_user_settings_to_psql(update.effective_user.id, context.user_data)

    await settings_method(update, context)


async def settings_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)
    current_method = context.user_data.get('method', DEFAULT_METHOD)

    keyboard = [
        [InlineKeyboardButton(
            f"→ {LANG_TEXTS[current_language]["method_euler"]} ←",
            callback_data="method_euler")
            if current_method == "method_euler" else InlineKeyboardButton(
                LANG_TEXTS[current_language]["method_euler"],
                callback_data="method_euler")],
        [InlineKeyboardButton(
            f"→ {LANG_TEXTS[current_language]["method_modified_euler"]} ←",
            callback_data="method_modified_euler")
            if current_method == "method_modified_euler" else InlineKeyboardButton(
                LANG_TEXTS[current_language]["method_modified_euler"],
                callback_data="method_modified_euler")],
        [InlineKeyboardButton(
            f"→ {LANG_TEXTS[current_language]["method_runge_kutta"]} ←",
            callback_data="method_runge_kutta")
            if current_method == "method_runge_kutta" else InlineKeyboardButton(
                LANG_TEXTS[current_language]["method_runge_kutta"],
                callback_data="method_runge_kutta")],
        [InlineKeyboardButton(
            f"→ {LANG_TEXTS[current_language]["method_dormand_prince"]} ←",
            callback_data="method_dormand_prince")
            if current_method == "method_dormand_prince" else InlineKeyboardButton(
                LANG_TEXTS[current_language]["method_dormand_prince"],
                callback_data="method_dormand_prince")],
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["back"],
            callback_data="settings_back")]
    ]

    new_text = LANG_TEXTS[current_language]["settings_menu"]
    new_reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message.text != new_text or query.message.reply_markup != new_reply_markup:
        await query.edit_message_text(
            new_text,
            reply_markup=new_reply_markup
        )

    return MENU


async def rounding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_rounding = query.data
    context.user_data['rounding'] = current_rounding

    await save_user_settings_to_psql(update.effective_user.id, context.user_data)

    await settings_rounding(update, context)


async def settings_rounding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)
    current_rounding = context.user_data.get('rounding', DEFAULT_ROUNDING)

    keyboard = [
        [
            InlineKeyboardButton(
                "→ 4 ←", callback_data="4") 
                if current_rounding == "4" else InlineKeyboardButton(
                    "4", callback_data="4"),
            InlineKeyboardButton(
                "→ 6 ←", callback_data="6") 
                if current_rounding == "6" else InlineKeyboardButton(
                    "6", callback_data="6"),
            InlineKeyboardButton(
                "→ 8 ←", callback_data="8") 
                if current_rounding == "8" else InlineKeyboardButton(
                    "8", callback_data="8"),
        ],
        [InlineKeyboardButton(
            f"→ {LANG_TEXTS[current_language]["without_rounding"]} ←",
            callback_data="16")
            if current_rounding == "16" else InlineKeyboardButton(
                LANG_TEXTS[current_language]["without_rounding"],
                callback_data="16")],
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["back"],
            callback_data="settings_back")]
    ]

    new_text = LANG_TEXTS[current_language]["settings_menu"]
    new_reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message.text != new_text or query.message.reply_markup != new_reply_markup:
        await query.edit_message_text(
            new_text,
            reply_markup=new_reply_markup
        )

    return MENU


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_language = query.data
    context.user_data['language'] = current_language

    await save_user_settings_to_psql(update.effective_user.id, context.user_data)

    await settings_language(update, context)


async def settings_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    keyboard = [
        [InlineKeyboardButton(
            "→ English ←", callback_data="en") 
            if current_language == "en" else InlineKeyboardButton(
                "English", callback_data="en")],
        [InlineKeyboardButton(
            "→ Русский ←", callback_data="ru") 
            if current_language == "ru" else InlineKeyboardButton(
                "Русский", callback_data="ru")],
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["back"],
            callback_data="settings_back")]
    ]

    new_text = LANG_TEXTS[current_language]["settings_menu"]
    new_reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message.text != new_text or query.message.reply_markup != new_reply_markup:
        await query.edit_message_text(
            new_text,
            reply_markup=new_reply_markup
        )

    return MENU


async def solve_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    keyboard = [
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["back"],
            callback_data="back")]
    ]

    new_text = LANG_TEXTS[current_language]["solve_history_menu"]
    new_reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message.text != new_text or query.message.reply_markup != new_reply_markup:
        await query.edit_message_text(
            new_text,
            reply_markup=new_reply_markup
        )

    return MENU


async def solve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user

    current_method = context.user_data.get('method', DEFAULT_METHOD)
    current_rounding = context.user_data.get('rounding', DEFAULT_ROUNDING)
    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    logger.info("Method of %s: %s", user.id, current_method)
    logger.info("Rounding of %s: %s", user.id, current_rounding)

    context.user_data['state'] = EQUATION

    if query.message and query.message.text:
        await query.edit_message_text(
            LANG_TEXTS[current_language]["enter_equation"]
        )
    else:
        await query.message.reply_text(
            LANG_TEXTS[current_language]["enter_equation"]
        )

    return EQUATION


async def equation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message:
        return EQUATION

    user = update.message.from_user
    logger.info("Equation of %s: %s", user.id, update.message.text)

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    is_valid_symbols, error_message = validate_symbols(update.message.text)
    if not is_valid_symbols:
        logger.info("User %s used unsupported symbol: %s", user.id, error_message)
        await update.message.reply_text(
            LANG_TEXTS[current_language]['symbols_error'] +
            f"<b><i>{error_message}</i></b>. " +
            LANG_TEXTS[current_language]['try_again'],
            parse_mode="HTML"
        )
        return EQUATION

    if not validate_parentheses(update.message.text):
        logger.info("User %s used incorrect parentheses.", user.id)
        await update.message.reply_text(
            LANG_TEXTS[current_language]["parentheses_error"] + " " +
            LANG_TEXTS[current_language]["try_again"]
        )
        return EQUATION

    formatted_equation, order = format_equation(update.message.text)

    if formatted_equation is None or order is None or order == 0:
        logger.info("User %s used unsupported symbols.", user.id)
        await update.message.reply_text(
            LANG_TEXTS[current_language]["equation_error"] + " " +
            LANG_TEXTS[current_language]["try_again"]
        )
        return EQUATION

    logger.info("Formatted Equation of %s: %s", user.id, formatted_equation)
    logger.info("Order of %s: %s", user.id, order)

    context.user_data['equation'] = formatted_equation
    context.user_data['order'] = order
    context.user_data['state'] = INITIAL_X

    await update.message.reply_text(
        LANG_TEXTS[current_language]["enter_x"])

    return INITIAL_X


async def initial_x(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message:
        return INITIAL_X

    user = update.message.from_user
    user_input = update.message.text.strip()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    try:
        float(user_input)
    except ValueError:
        logger.info("Invalid initial x input by %s: %s", user.id, user_input)
        await update.message.reply_text(
            LANG_TEXTS[current_language]["invalid_initial_x"] + " " +
            LANG_TEXTS[current_language]["try_again"]
        )
        return INITIAL_X

    logger.info("Initial x of %s: %s", user.id, user_input)

    context.user_data['initial_x'] = user_input
    context.user_data['state'] = INITIAL_Y

    if int(context.user_data['order']) == 1:
        await update.message.reply_text(
            LANG_TEXTS[current_language]["enter_y"]
        )
        return INITIAL_Y
    else:
        await update.message.reply_text(
            LANG_TEXTS[current_language]["enter_y_multiple"]
        )

    return INITIAL_Y


async def initial_y(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message:
        return INITIAL_Y

    user = update.message.from_user
    user_input = update.message.text.strip()

    inputs = user_input.split()
    order = int(context.user_data['order'])

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    try:
        [float(value) for value in inputs]
    except ValueError:
        invalid_value = next(
            (
                value for value in inputs
                if not value.replace('.', '', 1).replace('-', '', 1).isdigit()
            ),
            None
        )
        logger.info("Invalid initial y input by %s: %s", user.id, user_input)
        await update.message.reply_text(
            LANG_TEXTS[current_language]["invalid_initial_y"] +
            f"<b><i>{invalid_value}</i></b>. " +
            LANG_TEXTS[current_language]["try_again"],
            parse_mode="HTML"
        )
        return INITIAL_Y

    if len(inputs) != order:
        logger.info("Invalid number of initial y values by %s: %s", user.id, user_input)
        await update.message.reply_text(
            LANG_TEXTS[current_language]["invalid_initial_y_count1"] +
            f"<b><i>{len(inputs)}</i></b>. " +
            LANG_TEXTS[current_language]["invalid_initial_y_count2"] +
            f"<b><i>{order}</i></b>. " +
            LANG_TEXTS[current_language]["try_again"],
            parse_mode="HTML"
        )
        return INITIAL_Y

    logger.info("Initial y of %s: %s", user.id, user_input)
    context.user_data['initial_y'] = user_input
    context.user_data['state'] = REACH_POINT
    await update.message.reply_text(
        LANG_TEXTS[current_language]["enter_reach_point"])

    return REACH_POINT


async def reach_point(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message:
        return REACH_POINT

    user = update.message.from_user
    user_input = update.message.text.strip()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    try:
        float(user_input)
    except ValueError:
        logger.info("Invalid reach point input by %s: %s", user.id, user_input)
        await update.message.reply_text(
            LANG_TEXTS[current_language]["invalid_reach_point"] + " " +
            LANG_TEXTS[current_language]["try_again"]
        )
        return REACH_POINT

    logger.info("Reach point of %s: %s", user.id, user_input)
    context.user_data['reach_point'] = user_input
    context.user_data['state'] = STEP_SIZE
    await update.message.reply_text(
        LANG_TEXTS[current_language]["enter_step_size"])

    return STEP_SIZE


async def step_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message:
        return STEP_SIZE

    user = update.message.from_user
    user_input = update.message.text.strip()

    current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

    try:
        float(user_input)
    except ValueError:
        logger.info("Invalid step size input by %s: %s", user.id, user_input)
        await update.message.reply_text(
            LANG_TEXTS[current_language]["invalid_step_size"] + " " +
            LANG_TEXTS[current_language]["try_again"]
        )
        return STEP_SIZE

    logger.info("Step size of %s: %s", user.id, user_input)
    context.user_data['step_size'] = user_input

    result = await get_solution(context)

    keyboard = [
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["solve_over"],
            callback_data="solve")],
        [InlineKeyboardButton(
            LANG_TEXTS[current_language]["menu"],
            callback_data="menu")]
    ]

    new_reply_markup = InlineKeyboardMarkup(keyboard)

    if result is None:
        logger.info("User %s used unsupported symbols.", user.id)

        await save_user_settings(context)

        await update.message.reply_text(
            LANG_TEXTS[current_language]["data_error"] + " " +
            LANG_TEXTS[current_language]["try_again"],
            reply_markup=new_reply_markup
        )
        return MENU

    plot_graph = plot_solution(get_x_values(),
                               get_y_values(),
                               context.user_data['order'])

    print_result_info = get_result_info(result,
                                        context.user_data['order'],
                                        context.user_data['rounding'])

    logger.info("Result of %s: %s", user.id, print_result_info)

    await update.message.reply_photo(
        photo=plot_graph,
        caption=print_result_info,
        reply_markup=new_reply_markup
    )
    plot_graph.close()

    await save_user_settings(context)

    return MENU


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_state = context.user_data.get("state", None)

    if current_state in [EQUATION, INITIAL_X, INITIAL_Y, REACH_POINT, STEP_SIZE]:
        user = update.message.from_user
        logger.info("User %s canceled solving.", user.id)

        await save_user_settings(context)

        current_language = context.user_data.get('language', DEFAULT_LANGUAGE)

        keyboard = [
            [InlineKeyboardButton(
                LANG_TEXTS[current_language]["solve_over"],
                callback_data="solve")],
            [InlineKeyboardButton(
                LANG_TEXTS[current_language]["menu"],
                callback_data="menu")]
        ]

        new_reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            LANG_TEXTS[current_language]["cancel"],
            reply_markup=new_reply_markup
        )
        return MENU
    else:
        if update.message:
            await update.message.delete()
        return current_state


async def save_user_settings(context: ContextTypes.DEFAULT_TYPE):
    keys_to_keep = ['method', 'rounding', 'language']
    for key in list(context.user_data.keys()):
        if key not in keys_to_keep:
            del context.user_data[key]


async def save_user_settings_to_psql(user_id: int, user_settings: dict):
    with psql.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO user_settings (id, language, rounding, method)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET language = EXCLUDED.language,
                rounding = EXCLUDED.rounding,
                method = EXCLUDED.method;
            """,
            (
                user_id,
                user_settings.get('language', DEFAULT_LANGUAGE),
                user_settings.get('rounding', DEFAULT_ROUNDING),
                user_settings.get('method', DEFAULT_METHOD),
            )
        )
        psql.commit()


async def get_user_settings_from_psql(user_id: int) -> dict:
    with psql.cursor() as cursor:
        cursor.execute(
            """
            SELECT language, rounding, method
            FROM user_settings
            WHERE id = %s;
            """,
            (user_id,)
        )
        result = cursor.fetchone()
        if result:
            return {
                'language': result[0],
                'rounding': result[1],
                'method': result[2]
            }
        else:
            return {
                'language': DEFAULT_LANGUAGE,
                'rounding': DEFAULT_ROUNDING,
                'method': DEFAULT_METHOD
            }


def main() -> None:
    application = Application.builder().token(CONFIG['TELEGRAM_TOKEN']).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU:
            [CallbackQueryHandler(solve, pattern="^solve$"),
             CallbackQueryHandler(solve_history, pattern="^solve_history$"),
             CallbackQueryHandler(start, pattern="^back$"),
             CallbackQueryHandler(start, pattern="^menu$"),
             CallbackQueryHandler(settings, pattern="^settings$"),
             CallbackQueryHandler(settings, pattern="^settings_back$"),
             CallbackQueryHandler(settings_method, pattern="^settings_method$"),
             CallbackQueryHandler(settings_rounding, pattern="^settings_rounding$"),
             CallbackQueryHandler(settings_language, pattern="^settings_language$"),
             CallbackQueryHandler(
                 method, pattern="^method_(euler|modified_euler|runge_kutta|dormand_prince)$"),
             CallbackQueryHandler(rounding, pattern="^(4|6|8|16)$"),
             CallbackQueryHandler(language, pattern="^(en|ru)$")],
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
        fallbacks=[CommandHandler("cancel", cancel),
                   CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
