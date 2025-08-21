import psycopg2
from internish.settings import config_database

DB_HOST = config_database.DB_HOST
DB_NAME = config_database.DB_NAME
DB_USER = config_database.DB_USER
DB_PASSWORD = config_database.DB_PASSWORD
DB_PORT = config_database.DB_PORT

class PostgresConnection:
    def __init__(self):
        self.conn = None

    def to_json(self, cursor, result):
        if result is None:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        
        if isinstance(result, list):  
            return [dict(zip(columns, row)) for row in result]
        else: 
            return dict(zip(columns, result))
        
    def connect(self):
        if self.conn is None or self.conn.closed:
            self.conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
        return self.conn

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    def execute(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()

    def fetchone(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return self.to_json(cur, result)

    def fetchall(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(query, params)
            result = cur.fetchall()
            return self.to_json(cur, result)

    def insert(self, query, params=None):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                try:
                    return self.to_json(cur, cur.fetchone())

                except:
                    return None
                
        except Exception as e:
            conn.rollback()
            raise e

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

db = PostgresConnection()