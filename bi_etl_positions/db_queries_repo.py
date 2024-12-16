SELECT_QUERIES_REPOSITORY = {
    "get_active_ids": {
        "ids": "select rp.pos_no as ids from opening o join req_positions rp on rp.req_id = o.opening_id where o.confidential is false and o.status_id in(3,4,5) order by rp.pos_no;"
    },
    "etl_queries": {
        "get_data": "WITH req_approval_dates AS( SELECT osh.opening_id, MIN(osh.state_enter_date) AS req_approved_on FROM open_state_hist osh WHERE osh.status_id = 3 GROUP BY osh.opening_id), pos_approval_dates AS ( SELECT osh.opening_id, osh.position_id, MIN(osh.state_enter_date) AS pos_approved_on FROM open_state_hist osh WHERE osh.status_id = 3 GROUP BY osh.opening_id, osh.position_id ) SELECT rp.pos_no AS pid, rp.req_id AS rid, bu.bu_name AS org_unit_name, ol.location_group, ol.office AS location, o.employment_type, jl.jl_name, cs.cr_stream_name AS cs_name, o.skill_family, CONCAT(e.first_name, ' ', e.last_name) AS hm_name, CONCAT(e2.first_name, ' ', e2.last_name) AS ta_spoc_name, TO_CHAR(ra.req_approved_on, 'YYYY-MM-DD') AS req_approved_on, TO_CHAR(pa.pos_approved_on, 'YYYY-MM-DD') AS pos_approved_on, s.status_name AS req_current_step, s2.status_name AS pos_current_step, rp.archival_reason AS closure_reason, o.bu_id FROM req_positions rp JOIN opening o ON o.opening_id = rp.req_id JOIN business_unit bu ON bu.bu_id = o.bu_id JOIN office_location ol ON ol.location_id = rp.location_id  JOIN job_level jl ON jl.jl_id = o.jl_id JOIN career_stream cs ON cs.cr_stream_id = o.cr_stream_id JOIN employee e ON e.employee_id = o.hiring_manager_emp_id JOIN employee e2 ON e2.employee_id = o.coordinator_employee_id JOIN status s ON s.status_id = o.status_id JOIN status s2 ON s2.status_id = rp.approved_status LEFT JOIN req_approval_dates ra ON ra.opening_id = rp.req_id LEFT JOIN pos_approval_dates pa ON pa.opening_id = rp.req_id AND pa.position_id = rp.pos_no WHERE rp.pos_no IN {idsFilter};"
}}

COLUMNS_REPOSITORY = {
    "anchor_column": {"column_name": "pid"},
    "columns_names_and_dtype": {
        "pid": {"datatype": "int", "default_value": 0},
        "rid": {"datatype": "int", "default_value": 0},
        "org_unit_name": {"datatype": "str", "default_value": ""},
        "location_group": {"datatype": "str", "default_value": ""},
        "location": {"datatype": "str", "default_value": ""},
        "employment_type": {"datatype": "str", "default_value": ""},
        "jl_name": {"datatype": "str", "default_value": ""},
        "cs_name": {"datatype": "str", "default_value": ""},
        "skill_family": {"datatype": "str", "default_value": ""},
        "hm_name": {"datatype": "str", "default_value": ""},
        "ta_spoc_name": {"datatype": "str", "default_value": ""},
        "req_approved_on": {"datatype": "date", "default_value": None},
        "pos_approved_on": {"datatype": "date", "default_value": None},
        "req_current_step": {"datatype": "str", "default_value": ""},
        "pos_current_step": {"datatype": "str", "default_value": ""},
        "closure_reason": {"datatype": "str", "default_value": None},
        "bu_id": {"datatype": "int", "default_value": 0}
    }
}

UPDATE_QUERIES_REPOSITORY = {
    "insert_update_query": """INSERT INTO {schema_name}.position ({columns}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
    ON CONFLICT (pid) DO UPDATE SET {update_columns};"""
}
