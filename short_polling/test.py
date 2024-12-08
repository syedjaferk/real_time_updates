import sqlite3

# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect('messages.db')
    return conn

def insert_message(user_id, message):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (user_id, message) VALUES (?, ?)', (user_id, message))
    conn.commit()
    conn.close()

insert_message(1, "Hello, Jafer! Happy Morning")