import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', 3306)),
    'database': os.getenv('DATABASE_NAME', 'homeder'),
    'user': os.getenv('DATABASE_USER', 'bot'),
    'password': os.getenv('DATABASE_PASSWORD', 'Mama1946!')
}

def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None
    return None
