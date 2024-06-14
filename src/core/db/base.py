import json
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# from cachetools.func import ttl_cache
from mysql.connector import pooling

from src.entities.pos_schedule import PosSchedule
from src.util.constants import MYSQL_INFO

## 임시 .env 설정
load_dotenv()
conn_info = MYSQL_INFO.get(os.getenv("ENV"))
pool = pooling.MySQLConnectionPool(
    pool_name="crawler_pos_pool", pool_size=32, pool_reset_session=True, database="securities_info", **conn_info
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


def upsert_pos_schedule(args: List[PosSchedule]):
    base_query = """
       INSERT INTO pos_schedule (id, pos_name, pos_start_date, pos_end_date, pos_confirmed_price,
       pos_desired_min_price, pos_desired_max_price, pos_competition_rate, pos_taken_company)
       VALUES
       """

    # Generate the values part of the query
    values_list = []
    for schedule in args:
        values = (
            schedule.id,
            schedule.pos_name,
            schedule.pos_start_date.strftime("%Y-%m-%d"),
            schedule.pos_end_date.strftime("%Y-%m-%d"),
            schedule.pos_confirmed_price if schedule.pos_confirmed_price else 'NULL',
            schedule.pos_desired_min_price,
            schedule.pos_desired_max_price,
            schedule.pos_competition_rate if schedule.pos_competition_rate else 'NULL',
            schedule.pos_taken_company
        )
        values_str = "('{}', '{}', '{}', '{}', {}, {}, {}, {},'{}')".format(*values)
        values_list.append(values_str)

    # Join all values into a single string
    values_query = ",\n".join(values_list)

    # Combine base query with values
    final_query = base_query + values_query + """
    ON DUPLICATE KEY UPDATE
        pos_start_date = VALUES(pos_start_date),
        pos_end_date = VALUES(pos_end_date),
        pos_confirmed_price = VALUES(pos_confirmed_price),
        pos_desired_min_price = VALUES(pos_desired_min_price),
        pos_desired_max_price = VALUES(pos_desired_max_price),
        pos_competition_rate = VALUES(pos_competition_rate),
        pos_taken_company = VALUES(pos_taken_company);
    """
    return execute_query(final_query)
