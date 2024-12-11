from main import etl_runner
from custom_logging import logger
import time


def lambda_handler(event: dict, context: dict):
    logger.info(f"Received event: {event}")
    start_time = time.time()
    src_schema_name = event.get('schema_name')
    dst_schema_name = event.get('schema_name')
    client_id = event.get('client_id')
    try:
        results = etl_runner(src_schema_name, dst_schema_name)
        return {
            "statusCode": 200,
            "jobStatus": "Success",
            "clientId": client_id,
            "clientName": event.get('client_name'),
            "completedTime": str(time.time()),
            "schemaName": src_schema_name,
            "timeTaken": time.time() - start_time,
            "message": results}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {
            "statusCode": 400,
            "jobStatus": "Failed",
            "message": str(e),
            "clientId": client_id,
            "clientName": event.get('client_name'),
            "completedTime": time.time() - start_time,
            "schemaName": src_schema_name
        }
