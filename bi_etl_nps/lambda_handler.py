from main import etl_runner
from custom_logging import logger
import time
import asyncio

async def lambda_handler(event: dict, context: dict):
    logger.info(f"Received event: {event}")
    start_time = time.time()
    src_schema_name = event.get('scrSchemaName')
    dst_schema_name = event.get('dstSchemaName')
    client_id = event.get('clientId')
    try:
        results = await etl_runner(src_schema_name, dst_schema_name)
        return {"jobStatus": "Success",
                "clientId": client_id,
                "completedTime":  str(time.time()),
                "schemaName": src_schema_name,
                "timeTaken": time.time() - start_time,
                "message": results}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"jobStatus": "Failed",
                "error": str(e),
                "clientId": client_id,
                "completedTime":  str(time.time()),
                "schemaName": src_schema_name}
