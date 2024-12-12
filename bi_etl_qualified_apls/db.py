import psycopg2
from psycopg2 import pool
from custom_logging import logger
import os

SRC_POOL = None
TGT_POOL = None

# Fetch environment variables
SRC_HOST = os.environ.get('SRC_HOST', '').strip()
SRC_PASSWORD = os.environ.get('SRC_PASSWORD', '').strip()
SRC_USER = os.environ.get('SRC_USER', '').strip()
TGT_HOST = os.environ.get('TGT_HOST', '').strip()
TGT_PASSWORD = os.environ.get('TGT_PASSWORD', '').strip()
TGT_USER = os.environ.get('TGT_USER', '').strip()


def create_src_pool():
    global SRC_POOL
    try:
        SRC_POOL = psycopg2.pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=4,
            user=SRC_USER,
            password=SRC_PASSWORD,
            database="smaclifydb",
            host=SRC_HOST
        )
        return SRC_POOL
    except Exception as e:
        logger.error(f"Error creating source pool: {e}")
        raise Exception("Error creating source connection pool") from e


if not SRC_POOL:
    create_src_pool()
    logger.info("Source connection pool created successfully")


def create_tgt_pool():
    global TGT_POOL
    try:
        if not TGT_POOL:
            TGT_POOL = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=4,
                user=TGT_USER,
                password=TGT_PASSWORD,
                database="smaclify_bi_db",
                host=TGT_HOST
            )
        return TGT_POOL
    except Exception as e:
        logger.error(f"Error creating target pool: {e}")
        raise Exception("Error creating target connection pool") from e


if not TGT_POOL:
    create_tgt_pool()
    logger.info("Target connection pool created successfully")


def fetch_records_from_db(query: str, schema_name: str):
    connection = None
    try:
        connection = SRC_POOL.getconn()
        with connection.cursor() as cursor:
            if schema_name:
                cursor.execute(f"SET search_path TO {schema_name};")
            else:
                raise ValueError("Schema name (tenant identifier) is mandatory")

            cursor.execute(query)
            records = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            return records, column_names
    except Exception as e:
        logger.error(f"Error fetching records: {e}, Query: {query}")
        raise Exception(f"Error fetching records: {e}")
    finally:
        if connection:
            SRC_POOL.putconn(connection)


def insert_records_in_db(query: str, schema_name: str, values: list):
    connection = None
    try:
        connection = TGT_POOL.getconn()
        with connection.cursor() as cursor:
            if schema_name:
                cursor.execute(f"SET search_path TO {schema_name};")
            else:
                raise ValueError("Schema name (tenant identifier) is mandatory")

            cursor.executemany(query, values)
            connection.commit()
            return cursor.rowcount
    except Exception as e:
        logger.error(f"Error inserting records: {e}, Query: {query}")
        raise Exception(f"Error inserting records: {e}")
    finally:
        if connection:
            TGT_POOL.putconn(connection)
