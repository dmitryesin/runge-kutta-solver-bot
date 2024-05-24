import numpy as np
import sympy as sp

from py4j.java_gateway import JavaGateway
from logger import logger
from mathematics.functions import replace_math_functions
from mathematics.equations import check_alphabet
from plotting.plotter import plot_solution
from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

gateway = JavaGateway()

java_server = gateway.entry_point


async def get_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    The function goes through all the checks
    and if everything is successful, it returns the result.
    """
    user = update.message.from_user

    order, equation, initial_x, initial_y, reach_point, step_size = await extract_user_data(context)

    if not await check_equation_symbols(update, equation, order):
        return None

    if not await check_equation_validity(update, equation):
        return None

    try:
        set_java_parameters(order, equation, initial_x, initial_y, reach_point, step_size)
        result = java_server.getSolution()
    except ValueError as e:
        logger.error("User %s got error: %s", user.id, e)
        await update.message.reply_text(
            "An error occurred, check the values."
        )
        return None

    return result


async def extract_user_data(context: ContextTypes.DEFAULT_TYPE):
    """
    The function returns all values entered by the user.
    """
    data = context.user_data

    return (
        data['order'],
        data['equation'],
        data['initial_x'],
        data['initial_y'],
        data['reach_point'],
        data['step_size']
    )


async def check_equation_symbols(update: Update, equation, order):
    """
    The function takes the equation and its order
    and checks that the alphabet in the equation is correct.
    """
    user = update.message.from_user

    if not check_alphabet(equation, order):
        logger.error("User %s used unsupported symbols", user.id)
        await update.message.reply_text(
            "An error occurred, unsupported symbols found in the equation."
        )
        return False
    return True


async def check_equation_validity(update: Update, equation):
    """
    The function takes an equation and its order
    and checks for incorrect symbols in the equation.
    """
    user = update.message.from_user

    try:
        sp.sympify(replace_math_functions(equation))
        return True
    except (sp.SympifyError, Exception) as e:
        logger.error("User %s got error: %s", user.id, e)
        await update.message.reply_text(
            "An error occurred, check the equation."
        )
        return False


def set_java_parameters(order, equation, initial_x, initial_y, reach_point, step_size):
    """
    A function that passes user-entered parameters
    to the Java server.
    """
    java_server.setOrder(1 if order == "First" else 2)
    java_server.setEquation(str(replace_math_functions(equation)))
    java_server.setInitialX(float(initial_x))
    if order == "First":
        java_server.setInitialY(float(initial_y))
    elif order == "Second":
        initial_y1, initial_y2 = map(float, initial_y.split())
        java_server.setInitialY(initial_y1, initial_y2)
    java_server.setReachPoint(float(reach_point))
    java_server.setStepSize(float(step_size))


async def calc_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    The function retrieves the result if there is one.
    It also receives values for plotting the graph
    from Java server and plots it.
    """
    user = update.message.from_user

    result = await get_solution(update, context)

    if result is None:
        context.user_data.clear()
        return ConversationHandler.END

    x_values = np.array(java_server.getXValues())
    y_values = np.array(java_server.getYValues())

    plot_graph = plot_solution(x_values, y_values)

    print_result_info = get_result_info(result, context.user_data['order'])

    logger.info("Result of %s: %s", user.id, print_result_info)
    await update.message.reply_photo(
        photo=plot_graph,
        caption=print_result_info
    )
    plot_graph.close()


def get_result_info(result, order):
    """
    The function takes the result
    and order of the differential equation
    and returns the correct output of the answer.
    """
    if order == "First":
        return f"x: {result[0]:.2f}, y: {result[1]:.4f}"
    elif order == "Second":
        return f"x: {result[0]:.2f}, y: {result[1]:.4f}, z: {result[2]:.4f}"
    else:
        return ""
