from db_queries_repo import SELECT_QUERIES_REPOSITORY, UPDATE_QUERIES_REPOSITORY, \
    COLUMNS_REPOSITORY
from db import fetch_records_from_db, insert_records_in_db
import asyncio
from collections import defaultdict
from custom_logging import logger
from datetime import datetime
from tqdm import tqdm

async def build_queries(batch: str) -> list:
    temp_dict = dict()
    queries_dict = SELECT_QUERIES_REPOSITORY.get('etl_queries')
    for key, value in queries_dict.items():
        temp_dict[key] = value.format(idsFilter=batch)
    return list(temp_dict.values())


async def merge_data(anchor_column: str, extracted_data: tuple) -> list:
    merged_data = defaultdict(dict)
    for data_list in extracted_data:
        for obj in data_list:
            anchor_value = obj.get(anchor_column)
            if anchor_value is not None:
                merged_data[anchor_value].update(obj)
    result = list(merged_data.values())
    return result


async def fill_data(extracted_data: list) -> list:
    try:
        columns_repo = COLUMNS_REPOSITORY.get('columns_names_and_dtype')
        default_values = {column: meta['default_value'] for column, meta in columns_repo.items()}

        for record in extracted_data:
            for column_name, default_value in default_values.items():
                if record.get(column_name) is None:
                    record[column_name] = default_value

        return extracted_data
    except Exception as e:
        logger.error(f"Error filling data: {e}")
        print(f"Error filling data as: {e}")


async def transform_data_types(filled_data: list) -> list:
    try:
        columns_repo = COLUMNS_REPOSITORY.get('columns_names_and_dtype')
        for record in filled_data:
            for column_name, column_type_object in columns_repo.items():
                column_type = column_type_object.get('datatype')
                match column_type:
                    case 'str':
                        record[column_name] = record[column_name]
                    case 'int':
                        if record[column_name] is None:
                            record[column_name] = None
                        record[column_name] = int(record[column_name])
                    case 'float':
                        record[column_name] = record[column_name]
                    case 'boolean':
                        match str(record[column_name]).lower():
                            case 'true':
                                record[column_name] = True
                            case 'false':
                                record[column_name] = False
                    case 'date':
                        try:
                            record[column_name] = datetime.strptime(record[column_name], '%Y-%m-%d')
                        except:
                            record[column_name] = None
        return filled_data
    except Exception as e:
        logger.error(f"Error transforming data types: {e}")
        print(f"Error transforming data types as: {e}")


async def extract_data(schema_name: str, batch: list) -> tuple[list]:
    try:
        batch = str(tuple(batch)) if len(batch) > 1 else f"({batch[0]})"
        queries = await build_queries(batch)
        tasks = [fetch_records_from_db(query, schema_name) for query in queries]
        results = await asyncio.gather(*tasks)
        return results
    except Exception as e:
        logger.error(f"Error extracting data from db: {e}")


async def transform_data(extracted_data: tuple) -> list:
    anchor_column = COLUMNS_REPOSITORY.get('anchor_column').get('column_name')
    merged_data = await merge_data(anchor_column, extracted_data)
    filled_data = await fill_data(merged_data)
    transformed_date = await transform_data_types(filled_data)
    return transformed_date


async def load_data(schema_name, transformed_data):
    try:
        columns = list(COLUMNS_REPOSITORY.get('columns_names_and_dtype'))
        primary_key = COLUMNS_REPOSITORY.get('anchor_column').get('column_name')
        query = UPDATE_QUERIES_REPOSITORY.get('insert_update_query')
        update_columns = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key])
        values = [tuple(upload_dataset.get(col) for col in columns) for upload_dataset in transformed_data]
        query = query.format(schema_name=schema_name, columns=', '.join(columns),
                             update_columns=update_columns)
        await insert_records_in_db(query, schema_name, values)
        return {"jobStatus": "Success"}
    except Exception as e:
        logger.error(f"Error loading positions data in database: {e}")
        raise Exception(f"Error loading positions data in database: {e}")


async def etl_runner(src_schema_name: str, dst_schema_name: str):
    batch = []
    try:
        etl_results = []
        batch_size = 500
        records_list = await fetch_records_from_db(
            SELECT_QUERIES_REPOSITORY.get('get_active_ids').get('ids'), src_schema_name)
        etl_ids_list = [int(record.get('ids')) for record in records_list if len(records_list) > 0]

        if len(etl_ids_list) > 0:
            for index in tqdm(range(0, len(etl_ids_list), batch_size)):
                batch = [etl_id for etl_id in etl_ids_list[index:index + batch_size]]
                logger.debug(f"Processing batch starting at index {index}: {batch}")

                extracted_data = await extract_data(src_schema_name, batch)
                transformed_data = await transform_data(extracted_data)
                response = await load_data(dst_schema_name, transformed_data)
                etl_results.append(response)
        else:
            etl_results.append({"jobStatus": "Success"})
        return etl_results
    except Exception as e:
        logger.error(f"Error running qualifiedapps ETL: {e}, batches:{batch}")
        raise Exception(f"Error running qualifiedapps ETL: {e}, batches:{batch}")
