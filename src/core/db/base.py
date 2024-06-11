import json
import os
from typing import List

# from cachetools.func import ttl_cache
from mysql.connector import pooling

from src.util.constants import MYSQL_INFO

conn_info = MYSQL_INFO.get(os.getenv("env"))
pool = pooling.MySQLConnectionPool(
    pool_name="crawler_pos_pool", pool_size=32, pool_reset_session=True, database="pos", **conn_info
)


def get_results(query, *args):
    with pool.get_connection() as conn:
        cursor = conn.cursor(buffered=True)
        cursor.execute(query, *args)
        rows = cursor.fetchall()
        desc = [d[0] for d in cursor.description]
        return [] if rows is None else [Dotdict(dict(zip(desc, res))) for res in rows]


def get_result(query, *args):
    with pool.get_connection() as conn:
        cursor = conn.cursor(buffered=True)
        cursor.execute(query, *args)
        row = cursor.fetchone()
        desc = [d[0] for d in cursor.description]
        return None if row is None else Dotdict(dict(zip(desc, row)))


def execute_query(query, *args):
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, *args)
        return conn.commit()


def execute_query_many(query, *args):
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, *args)
        return conn.commit()


def execute_queries(queries: List[str], args: list):
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        for index, query in enumerate(queries):
            cursor.execute(query, args[index])
        return conn.commit()


def execute_queries_many(queries: List[str], args: list):
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        for index, query in enumerate(queries):
            cursor.executemany(query, args[index])
        return conn.commit()

class Dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def select_pos_schedules() -> List:
    return []