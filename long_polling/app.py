# server.py
from flask import Flask, jsonify
import sqlite3
import time
from datetime import datetime
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)

# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect('messages.db')
    return conn

# Initialize database and create table if not exists
def init_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Check if there is a new message for a user
def get_latest_message(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT message, timestamp FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


@app.route('/check-messages/<int:user_id>', methods=['GET'])
def check_messages(user_id):
    timeout = 10  # Long polling timeout (in seconds)
    poll_interval = 1  # Interval to check for new messages (in seconds)

    start_time = time.time()

    while time.time() - start_time < timeout:
        message = get_latest_message(user_id)
        
        if message:
            return jsonify({
                'message': message[0],
                'timestamp': message[1]
            }), 200

        # No new message, wait and try again
        time.sleep(poll_interval)

    # No new messages after timeout period
    return jsonify({
        'message': 'No new messages'
    }), 200

if __name__ == '__main__':
    app.run(debug=True)


