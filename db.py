import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="admin",
        password="0000",
        database="gym_diario"
    )
