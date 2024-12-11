import time
from custom_logging import logger
async def etl_runner(src_schema_name: str, dst_schema_name: str):
    try:
        for i in range(0, 10):
            time.sleep(1)
            logger.info(f"Running ETL for batch {i}")
        return "success"
    except Exception as e:
        logger.error(f"Error running positions ETL: {e}")
        raise Exception(f"Error running positions ETL: {e}")
