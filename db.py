import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def get_all_students():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM students")
            return cursor.fetchall()
    finally:
        conn.close()

def get_student_by_id(student_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            return cursor.fetchone()
    finally:
        conn.close()
