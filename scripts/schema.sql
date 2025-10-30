-- Drop existing tables
DROP TABLE IF EXISTS health_data;
DROP TABLE IF EXISTS session;

-- Sessions
CREATE TABLE session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key TEXT UNIQUE NOT NULL,
    start_time INTEGER NOT NULL
);

-- Health data (linked to a session)
CREATE TABLE health_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    spo2 INTEGER NOT NULL,
    pulse INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES session (id)
);

-- Create index for faster session lookups
CREATE INDEX idx_session_key ON session(session_key);
