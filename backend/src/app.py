from flask import Flask, jsonify, abort
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3
import os
import time
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Number of readings to return
LIMIT_READINGS = 50

# Database path
db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "database.db")
db_path = os.path.abspath(db_path)

# Set tracking all active sessions
active_sessions = set()
# Track last timestamp per session instead of globally
session_timestamps = {}

def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_session_data(session_key):
    """Get the most recent readings for a session."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            # First get session ID
            cursor.execute("SELECT id FROM session WHERE session_key = ?", (session_key,))
            session = cursor.fetchone()
            
            if not session:
                return None
                
            # Get latest health data for session
            cursor.execute("""
                SELECT timestamp, spo2, pulse 
                FROM health_data 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?""", (session['id'], LIMIT_READINGS))
            
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

@app.route("/data/<session_key>")
def get_data(session_key):
    """Return the most recent readings for a session as JSON."""
    data = get_session_data(session_key)
    if data is None:
        abort(404, description="Session not found")
    return jsonify(data)

@app.route("/")
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "Flask backend running"})

# --- SocketIO events ---
@socketio.on("join")
def handle_join(data):
    """Handle client joining a specific session."""
    session_key = data.get('session')
    data = get_session_data(session_key)
    if data:
        active_sessions.add(session_key)
        # Initialize timestamp for this session
        session_timestamps[session_key] = 0
        print(f"Client joined session: {session_key}")
        emit(f"vitals_{session_key}", data)
    else:
        emit("error", {"message": "Session not found"})

@socketio.on("leave")
def handle_leave(data):
    session_key = data.get('session')
    active_sessions.discard(session_key)
    # Clean up timestamp when session ends
    session_timestamps.pop(session_key, None)
    print(f"Client left session: {session_key}")

def watch_db():
    """
    Continuously watches the database for new readings and pushes updates to clients.
    """    
    while True:
        try:
            # Only query if there are active sessions
            if active_sessions:
                with get_db() as conn:
                    cursor = conn.cursor()
                    
                    # Check each active session
                    for session_key in active_sessions.copy():
                        data = get_session_data(session_key)
                        if data:
                            last_ts = session_timestamps.get(session_key, 0)
                            if data[0]['timestamp'] > last_ts:
                                session_timestamps[session_key] = data[0]['timestamp']
                                socketio.emit(f"vitals_{session_key}", data)
                        else:
                            # Remove inactive/invalid sessions
                            active_sessions.discard(session_key)
                            session_timestamps.pop(session_key, None)
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        
        time.sleep(1)  # Check for new data every second

# Start the database watching thread
threading.Thread(target=watch_db, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, debug=True)
