import psycopg2
from psycopg2 import pool
from custom_logging import logger
import os
import boto3

SRC_POOL = None
TGT_POOL = None

iqaCredList = ["/iqa/serverless-mnh-bi-etl/smaclifydb/readonly/url",
               "/iqa/wowreports/smaclifydb/readonly/password",
               "/iqa/wowreports/smaclifydb/readonly/username",
               "/iqa/bi_etl/smaclify_bi_db/readwrite/password",
               "/iqa/bi_etl/smaclify_bi_db/readwrite/username"]

prodCredList = ["/prod/serverless-mnh-bi-etl/smaclifydb/readonly/url",
                "/prod/wowreports/smaclifydb/readonly/password",
                "/prod/wowreports/smaclifydb/readonly/username",
                "/prod/bi_etl/smaclify_bi_db/readwrite/password",
                "/prod/bi_etl/smaclify_bi_db/readwrite/username"]

ssm = boto3.client("ssm", region_name='us-west-2')
ETL_ENV = os.environ.get('ETL_ENV', '').strip()

if ETL_ENV == 'iqa':
    environment = iqaCredList
elif ETL_ENV == 'prod':
    environment = prodCredList
else:
    environment = []


def get_ssm_secret(parameter_name):
    return ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )


def create_src_pool(SRC_USER, SRC_PASSWORD, SRC_HOST):
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
    host = get_ssm_secret(environment[0])['Parameter']['Value']
    password = get_ssm_secret(environment[1])['Parameter']['Value']
    user = get_ssm_secret(environment[2])['Parameter']['Value']
    create_src_pool(host, password, user)
    logger.info("Source connection pool created successfully")


def create_tgt_pool(TGT_USER, TGT_PASSWORD, TGT_HOST):
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
    host = get_ssm_secret(environment[0])['Parameter']['Value']
    password = get_ssm_secret(environment[3])['Parameter']['Value']
    user = get_ssm_secret(environment[4])['Parameter']['Value']
    create_tgt_pool(host, password, user)
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
