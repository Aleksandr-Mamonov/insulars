import sqlite3

DB_PATH = "insulars.db"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_to_db():
    """Returns a db connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn


def execute_sql_query(sql: str, params: dict):
    """Executes a SQL query.
    Returns execution result and connection to db."""
    conn = connect_to_db()
    cur = conn.cursor()
    result = cur.execute(sql, params)
    return {"result": result, "connection": conn}


def select_one_from_db(sql: str, params: dict):
    """Fetches one record from db."""
    result = execute_sql_query(sql, params)
    return result["result"].fetchone()


def select_all_from_db(sql: str, params: dict):
    """Fetches all records from db."""
    result = execute_sql_query(sql, params)
    return result["result"].fetchall()


def write_to_db(sql: str, params: dict):
    """Executes a SQL query and commit changes to db."""
    result = execute_sql_query(sql, params)
    result["connection"].commit()


def strip_whitespaces_from_dict_values(d: dict) -> dict:
    updated_dict = {}
    for k, v in d.items():
        if isinstance(v, str):
            updated_dict[k] = "".join(v.split())
            continue
        updated_dict[k] = v
    return updated_dict
