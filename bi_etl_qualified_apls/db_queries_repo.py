SELECT_QUERIES_REPOSITORY = {
    "get_active_ids": {
        "ids": "select appln.app_id as ids from application appln join opening o on o.opening_id = appln.opening_id where o.confidential is false and o.status_id in(3,4,5) and appln.step_id >701 and appln.step_id<1301 order by appln.app_id ;"
    },
    "etl_queries": {
        "get_data": "with tts as( select appln.app_id, cast( greatest( extract(EPOCH from MIN(osh.state_enter_date)) * 1000 - extract(EPOCH from appln.created_date) * 1000, 0) as BIGINT) as time_difference from application appln join open_state_hist osh on osh.opening_id = appln.opening_id where osh.status_id = 3 and osh.position_id = 0 and appln.app_id in {idsFilter} group by appln.app_id), ttq as( select appln.app_id, greatest( extract(EPOCH from ash.state_change_date) * 1000 - extract(EPOCH from appln.created_date) * 1000, 0 )::BIGINT as time_difference from application appln join application_state_history ash on ash.app_id = appln.app_id where ash.to_step = 702 and ash.from_step = 701 and appln.app_id in {idsFilter} ), tte as( with min_eval_start as ( select application_id, MIN(eval_start_time) as min_eval_start_time from evaluation where status_id in (9001, 9002) and application_id in {idsFilter} group by application_id ) select appln.app_id, greatest( extract(EPOCH from ash.state_change_date) * 1000 - extract(EPOCH from min_eval.min_eval_start_time) * 1000, 0 )::BIGINT as time_difference from application appln join application_state_history ash on ash.app_id = appln.app_id join min_eval_start min_eval on min_eval.application_id = appln.app_id where ash.to_step = 702 and ash.from_step = 701 and appln.app_id in {idsFilter} ), tto as ( with max_eval_by_time as ( select application_id, MAX(eval_by_time) as max_eval_by_time from evaluation group by application_id ) select appln.app_id, greatest( extract(EPOCH from appln.offer_released_date) * 1000 - extract(EPOCH from max_eval.max_eval_by_time) * 1000, 0 )::BIGINT as time_difference from application appln join max_eval_by_time max_eval on max_eval.application_id = appln.app_id where appln.app_id in {idsFilter} ), ttob as ( select appln.app_id, greatest( cast(extract(EPOCH from appln.offer_acceptance_date) * 1000 as BIGINT) - cast(extract(EPOCH from appln.offer_released_date) * 1000 as BIGINT), 0 )::BIGINT as time_difference from application appln where appln.app_id in {idsFilter} ), ttj as ( select appln.app_id, greatest( cast(extract(EPOCH from appln.joined_date) * 1000 as BIGINT) - cast(extract(EPOCH from appln.offer_acceptance_date) * 1000 as BIGINT), 0 )::BIGINT as time_difference from application appln where appln.app_id in {idsFilter} ), pos as ( select rp.application_id, rp.pos_no from req_positions rp where rp.application_id in {idsFilter} ) select appln.opening_id as rid, pos.pos_no as pid, appln.app_id as apl_id, asd.applicant_source_title as src, asc2.app_source_cat_name as src_cat, s2.status_name as last_step_name, s.status_name as current_step_name, to_char(appln.joined_date, 'YYYY-MM-DD') as joining_date, tts.time_difference as tts, ttq.time_difference as ttq, tte.time_difference as tte, tto.time_difference as tto, ttob.time_difference as ttob, ttj.time_difference as ttj, aa.gender, o.bu_id from application appln join applicant_source_details asd on asd.applicant_source_id = appln.source_id join applicant_source_cat asc2 on asc2.app_source_cat_id = asd.app_source_cat_id join status s on s.status_id = appln.step_id join opening o on o.opening_id = appln.opening_id join status s2 on s2.status_id = (appln.app_meta_data::jsonb->'lastStepReached')::int join applicant_attributes aa on aa.applicant_id = appln.applicant_id left join tts on tts.app_id = appln.app_id left join ttq on ttq.app_id = appln.app_id left join tte on tte.app_id = appln.app_id left join tto on tto.app_id = appln.app_id left join ttob on ttob.app_id = appln.app_id left join ttj on ttj.app_id = appln.app_id left join pos on pos.application_id = appln.app_id where appln.app_id in {idsFilter}"
    }}

COLUMNS_REPOSITORY = {
    "anchor_column": {"column_name": "apl_id"},
    "columns_names_and_dtype": {
        "rid": {"datatype": "int", "default_value": 0},
        "pid": {"datatype": "int", "default_value": 0},
        "apl_id": {"datatype": "int", "default_value": 0},
        "src": {"datatype": "str", "default_value": ""},
        "src_cat": {"datatype": "str", "default_value": ""},
        "last_step_name": {"datatype": "str", "default_value": ""},
        "current_step_name": {"datatype": "str", "default_value": ""},
        "joining_date": {"datatype": "date", "default_value": None},
        "tts": {"datatype": "int", "default_value": 0},
        "ttq": {"datatype": "int", "default_value": 0},
        "tte": {"datatype": "int", "default_value": 0},
        "tto": {"datatype": "int", "default_value": 0},
        "ttob": {"datatype": "int", "default_value": 0},
        "ttj": {"datatype": "int", "default_value": 0},
        "gender": {"datatype": "str", "default_value": None},
        "bu_id": {"datatype": "int", "default_value": 0}
    }
}

UPDATE_QUERIES_REPOSITORY = {
    "insert_update_query": """INSERT INTO {schema_name}.qualified_apls ({columns}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (apl_id) DO UPDATE SET {update_columns};"""
}
