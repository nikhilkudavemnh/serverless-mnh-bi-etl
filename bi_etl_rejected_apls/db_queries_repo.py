SELECT_QUERIES_REPOSITORY = {
    "get_active_ids": {
        "ids": "select appln.app_id as ids from application appln join opening o on o.opening_id = appln.opening_id where appln.status_id = 13 and o.confidential is false order by appln.app_id;"
    },
    "etl_queries": {
        "get_data": "select appln.opening_id as rid, appln.app_id as apl_id, s.status_name as from_step, ae.exit_code as rejection_code, ae.exit_reason_category as rejection_reason, to_char(appln.last_status_change_date,'YYYY-MM-DD') as rejected_on from application appln join application_exit ae on ae.application_id = appln.app_id join status s on s.status_id = ae.from_step where appln.status_id =13 and appln.app_id in {idsFilter};"
}}

COLUMNS_REPOSITORY = {
    "anchor_column": {"column_name": "apl_id"},
    "columns_names_and_dtype": {
        "rid": {"datatype": "int", "default_value": 0},
        "apl_id": {"datatype": "int", "default_value": 0},
        "from_step": {"datatype": "str", "default_value": ""},
        "rejection_code": {"datatype": "str", "default_value": ""},
        "rejection_reason": {"datatype": "str", "default_value": ""},
        "rejected_on": {"datatype": "date", "default_value": None},
    }
}

UPDATE_QUERIES_REPOSITORY = {
    "insert_update_query": """INSERT INTO {schema_name}.rejected_apls ({columns}) VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (apl_id) DO UPDATE SET {update_columns};"""
}
