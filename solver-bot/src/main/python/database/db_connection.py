import psycopg2

from logger import logger

def get_psql_connection():
    try:
        return psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
    except psycopg2.OperationalError:
        logger.error("Failed to connect to database.")
        return None
