import psycopg2

from database.db_connection import get_psql_connection
from logger import logger

DEFAULT_METHOD = "method_runge_kutta"
DEFAULT_ROUNDING = "4"
DEFAULT_LANGUAGE = "en"

psql = get_psql_connection()

async def save_user_settings_to_psql(user_id: int, user_settings: dict):
    if psql is None:
        logger.warning("Database connection is not available. Skipping save operation.")
        return

    try:
        with psql.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (id, language, rounding, method)
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
    except psycopg2.Error:
        logger.error("Failed to save user settings to database.")


async def get_user_settings_from_psql(user_id: int) -> dict:
    if psql is None:
        logger.warning("Database connection is not available. Returning default user settings.")
        return {
            'language': DEFAULT_LANGUAGE,
            'rounding': DEFAULT_ROUNDING,
            'method': DEFAULT_METHOD
        }

    try:
        with psql.cursor() as cursor:
            cursor.execute(
                """
                SELECT language, rounding, method
                FROM users
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
    except psycopg2.Error:
        logger.error("Failed to fetch user settings from database.")

    return {
        'language': DEFAULT_LANGUAGE,
        'rounding': DEFAULT_ROUNDING,
        'method': DEFAULT_METHOD
    }
