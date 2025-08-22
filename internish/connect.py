# internish/connect.py
import psycopg2
from contextlib import contextmanager
from internish.settings import config_database

DB_HOST = config_database.DB_HOST
DB_NAME = config_database.DB_NAME
DB_USER = config_database.DB_USER
DB_PASSWORD = config_database.DB_PASSWORD
DB_PORT = config_database.DB_PORT

class PostgresConnection:
    def __init__(self):
        self.dsn = dict(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT
        )

    @staticmethod
    def _to_json(cursor, result):
        if result is None:
            return None
        cols = [d[0] for d in cursor.description]
        if isinstance(result, list):
            return [dict(zip(cols, row)) for row in result]
        return dict(zip(cols, result))

    @contextmanager
    def get_conn(self):
        conn = psycopg2.connect(**self.dsn)
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def get_cursor(self):
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                yield conn, cur

    def execute(self, query, params=None):
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            conn.commit()

    def fetchone(self, query, params=None):
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            row = cur.fetchone()
            return self._to_json(cur, row)

    def fetchall(self, query, params=None):
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            rows = cur.fetchall()
            return self._to_json(cur, rows)

    def insert(self, query, params=None):
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            try:
                row = cur.fetchone() 
                conn.commit()
                return self._to_json(cur, row)
            except psycopg2.ProgrammingError:
                conn.commit()
                return None

    def update(self, query, params=None):
        with self.get_cursor() as (conn, cur):
            cur.execute(query, params)
            try:
                row = cur.fetchone()
                conn.commit()
                return self._to_json(cur, row)
            except psycopg2.ProgrammingError:
                conn.commit()
                return None

    @contextmanager
    def transaction(self):
        with self.get_conn() as conn:
            try:
                with conn.cursor() as cur:
                    yield cur
                conn.commit()
            except Exception:
                conn.rollback()
                raise

db = PostgresConnection()
