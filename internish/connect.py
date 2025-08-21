import psycopg2
import internish.settings as settings

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
                dbname=settings.config_database.db_name,
                user=settings.config_database.db_user,
                password=settings.config_database.db_password,
                host=settings.config_database.db_host,
                port=settings.config_database.db_port
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
        
    def save_refresh(self, email, token, expires_at):
        query = """
        INSERT INTO refresh_tokens (user_email_, token_, expires_at_)
        VALUES (%s, %s, %s)
        RETURNING id_, user_email_, token_, expires_at_, revoked_, created_at_
        """
        return self.insert(query, (email, token, expires_at))

    def get_refresh(self, token):
        query = "SELECT * FROM refresh_tokens WHERE token_ = %s"
        return self.fetchone(query, (token,))

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

db = PostgresConnection()