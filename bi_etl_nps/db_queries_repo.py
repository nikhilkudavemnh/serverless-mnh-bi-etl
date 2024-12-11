SELECT_QUERIES_REPOSITORY = {
    "get_active_ids": {
        "ids": "select e.eval_id as ids from evaluation e join application appln on appln.app_id = e.application_id join opening o on o.opening_id = appln.opening_id where o.status_id in(3,4,5) and o.confidential is false order by e.eval_id;"
    },
    "etl_queries": {
        "get_data": "select a.opening_id as rid, a.app_id as apl_id, e.eval_id as eval_id, s.status_name as associated_step, e.applicant_nps as nps, case when e.applicant_nps>0 then true else false end as filled,case when e.applicant_nps >0 then to_char(e.eval_by_time,'YYYY-MM-DD') else null end as submitted_on from application a join evaluation e on e.application_id = a.app_id join status s on s.status_id = e.associated_step_id  where e.eval_id in {idsFilter};"
}}

COLUMNS_REPOSITORY = {
    "anchor_column": {"column_name": "eval_id"},
    "columns_names_and_dtype": {
        "eval_id": {"datatype": "int", "default_value": 0},
        "rid": {"datatype": "int", "default_value": 0},
        "apl_id": {"datatype": "int", "default_value": 0},
        "associated_step": {"datatype": "str", "default_value": ""},
        "nps": {"datatype": "int", "default_value": 0},
        "filled": {"datatype": "boolean", "default_value": False},
        "submitted_on": {"datatype": "date", "default_value": None},
    }
}

UPDATE_QUERIES_REPOSITORY = {
    "insert_update_query": """INSERT INTO {schema_name}.nps ({columns}) VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (eval_id) DO UPDATE SET {update_columns};"""
}
