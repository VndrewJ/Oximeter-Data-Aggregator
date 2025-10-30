from flask import Flask, jsonify, abort, request
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path) 

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
CORS(app)

# Initialize Supabase client
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@app.route("/session/new", methods=['POST'])
def create_session():
    """Create and return a new session key"""
    try:
        session_key = str(uuid.uuid4())[:6].upper()
        
        # Create session in Supabase
        result = supabase.table('sessions').insert({
            'session_key': session_key,
            'start_time': datetime.utcnow().isoformat()
        }).execute()
        
        return jsonify({
            'session_key': session_key,
            'message': 'Session created successfully'
        })
    except Exception as e:
        print(f"Error creating session: {e}")
        abort(500)

@app.route("/data/<session_key>")
def get_data(session_key):
    try:
        # Get session id
        session = supabase.table('sessions')\
            .select('id')\
            .eq('session_key', session_key)\
            .execute()\
            .data

        if not session:
            abort(404)

        # Get health data
        result = supabase.table('health_data')\
            .select('*')\
            .eq('session_id', session[0]['id'])\
            .order('timestamp', desc=True)\
            .limit(50)\
            .execute()

        return jsonify(result.data)
    except Exception as e:
        print(f"Error: {e}")
        abort(500)

if __name__ == "__main__":
    app.run(debug=True)
