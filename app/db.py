import os
import sqlite3

class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, args=None):
        # Replace MySQL style placeholders (%s) with SQLite style (?)
        query = query.replace('%s', '?')
        if args:
            return self.cursor.execute(query, args)
        return self.cursor.execute(query)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()
    
    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    def __getattr__(self, name):
        return getattr(self.cursor, name)

class SQLiteConnectionWrapper:
    def __init__(self, connection):
        self.connection = connection
    
    def cursor(self):
        return SQLiteCursorWrapper(self.connection.cursor())

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

def get_connection():
    db_type = os.environ.get("DB_TYPE", "mysql")
    
    if db_type == "sqlite":
        # Connect to SQLite database file
        conn = sqlite3.connect('gym_diario.db')
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries/objects
        return SQLiteConnectionWrapper(conn)
    else:
        # Default to MySQL
        import mysql.connector
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "admin"),
            password=os.environ.get("DB_PASSWORD", "0000"),
            database=os.environ.get("DB_NAME", "gym_diario")
        )
