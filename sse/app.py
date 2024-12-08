from flask import Flask, jsonify, Response, stream_with_context
import sqlite3
import time
import json
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)

# Connect to SQLite database
def connect_db():
    conn = sqlite3.connect('messages.db', check_same_thread=False)
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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                               message_sent TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()


# SSE endpoint to stream new messages for a user
@app.route('/stream-messages/<int:user_id>', methods=['GET'])
def stream_messages(user_id):
    @stream_with_context
    def message_stream():
        print("user id", user_id)
        last_seen_id = 0  # To keep track of the last message sent to the client
        conn = connect_db()
        
        while True:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, message, timestamp FROM messages WHERE user_id = ? AND id > ? ORDER BY timestamp ASC",
                (user_id, last_seen_id)
            )
            new_messages = cursor.fetchall()
            
            for msg in new_messages:
                last_seen_id = msg[0]
                yield f"data: {json.dumps({'message': msg[1], 'timestamp': msg[2]})}\n\n"
            
            time.sleep(2)  # Poll the database every 2 seconds

    return Response(message_stream(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
