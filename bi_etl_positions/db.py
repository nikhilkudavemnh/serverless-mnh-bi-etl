import asyncpg
from custom_logging import logger
import os
SRC_POOL = None
TGT_POOL = None
SRC_HOST = os.environ.get('SRC_HOST')
SRC_PASSWORD = os.environ.get('SRC_PASSWORD')
SRC_USER = os.environ.get('SRC_USER')
TGT_HOST = os.environ.get('TAR_HOST')
TGT_PASSWORD = os.environ.get('TAR_PASSWORD')
TGT_USER = os.environ.get('TAR_USER')

async def create_src_pool():
    global SRC_POOL
    try:
        if not SRC_POOL:
            SRC_POOL = await asyncpg.create_pool(
                user=SRC_USER,
                password=SRC_PASSWORD,
                database="smaclifydb",
                host=SRC_HOST,
                min_size=10,
                max_size=20
            )
        return SRC_POOL
    except Exception as e:
        logger.error(f"Error creating target pool: {e}")
        raise Exception("Error creating target pool")


async def create_tgt_pool():
    global TGT_POOL
    try:
        if not TGT_POOL:
            TGT_POOL = await asyncpg.create_pool(
                user=TGT_USER,
                password=TGT_PASSWORD,
                database="smaclify_bi_db",
                host=TGT_HOST,
                min_size=10,
                max_size=20
            )
        return TGT_POOL
    except Exception as e:
        logger.error(f"Error creating target pool: {e}")
        raise Exception("Error creating target pool")

async def fetch_records_from_db(query: str, schema_name: str):
    try:
        src_pool = await create_src_pool()
        async with src_pool.acquire() as connection:
            if schema_name:
                await connection.fetch(f"SET search_path to {schema_name};")
            else:
                raise Exception("Tenant identifier is mandatory")
            records = await connection.fetch(query)
            return [dict(record) for record in records] if records else []
    except Exception as e:
        logger.error(f"Error fetching records: {e}")

        print(f"Error fetching records as: {e}")
        print(query)
        raise Exception(f"Error fetching records as: {e}")


async def insert_records_in_db(query: str, schema_name: str, values: list):
    try:
        tgt_pool = await create_tgt_pool()
        async with tgt_pool.acquire() as connection:
            if schema_name:
                await connection.fetch(f"SET search_path to {schema_name};")
            else:
                raise Exception("Tenant identifier is mandatory")
            records = await connection.executemany(query, values)
            return records
    except Exception as e:
        logger.error(f"Error inserting records: {e}, query:{query}")
        raise Exception(f"Error inserting records as:{e}")
