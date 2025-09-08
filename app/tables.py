import psycopg2
from psycopg2 import errors

# Подключение к PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="Admin1994",
    host="localhost",
    port="5432"
)


# Создание курсора
cursor = conn.cursor()


try:
    cursor.execute("""
        CREATE TABLE users (
        id BIGINT PRIMARY KEY,
        is_waiter BOOL NULL DEFAULT FALSE
    );
    """)
    conn.commit()
    print("Таблица 'users' создана")

except errors.DuplicateTable:
    conn.rollback()
    print("Таблица 'users' уже существует, пропускаем создание")
