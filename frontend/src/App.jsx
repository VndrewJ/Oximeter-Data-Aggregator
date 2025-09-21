import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import './App.css';

const socket = io("http://localhost:5000/"); // connect to Flask-SocketIO

function Home() {
  const navigate = useNavigate();
  const [sessionKey, setSessionKey] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!sessionKey.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`http://localhost:5000/data/${sessionKey}`);
      if (!response.ok) {
        throw new Error('Invalid session key');
      }
      navigate(`/data/${sessionKey}`);
    } catch (err) {
      setError('Invalid session key. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <h1>Welcome to the IoT Oximeter Project</h1>
      <p>Enter your session key to view data:</p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={sessionKey}
          onChange={(e) => {
            setSessionKey(e.target.value.toUpperCase());
            setError(''); // Clear error when input changes
          }}
          placeholder="Enter session key"
          maxLength={6}
          style={{ marginRight: '10px' }}
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Checking...' : 'View Data'}
        </button>
      </form>
      {error && (
        <p style={{ color: 'red', marginTop: '10px' }}>
          {error}
        </p>
      )}
    </div>
  );
}

function DataPage() {
  const navigate = useNavigate();
  const [data, setData] = useState([]);
  const [error, setError] = useState(false);
  const sessionKey = window.location.pathname.split('/')[2]; // Get session key from URL

  // helper: ensure consistent formatting
  const formatBuffer = (buffer) =>
    buffer.map((row, i) => ({
      timestamp: Number(row["timestamp"]),
      spo2: Number(row["spo2"]),
      pulse: Number(row["pulse"]),
      idx: i
    }));

  useEffect(() => {
    if (!sessionKey) {
      navigate('/');
      return;
    }

    // 1. Fetch initial buffer from REST API with session key
    fetch(`http://localhost:5000/data/${sessionKey}`)
      .then((res) => {
        if (!res.ok) throw new Error('Session not found');
        return res.json();
      })
      .then((json) => setData(formatBuffer(json)))
      .catch(() => setError(true));

    // 2. Subscribe to websocket events for this session
    socket.emit('join', { session: sessionKey });
    
    socket.on(`vitals_${sessionKey}`, (buffer) => {
      setData(formatBuffer(buffer));
      setError(false);
    });

    socket.on("connect_error", () => {
      setError(true);
    });

    // cleanup
    return () => {
      socket.emit('leave', { session: sessionKey });
      socket.off(`vitals_${sessionKey}`);
      socket.off("connect_error");
    };
  }, [sessionKey, navigate]);

  const recentData = [...data].reverse();
  const tableData = recentData.slice(0, 20); // show last 20 entries in table

  return (
    <div>
      <h2>Session: {sessionKey}</h2>
      {error ? (
        <p style={{ color: 'red' }}>
          Error connecting to server. Please try again later.
        </p>
      ) : data.length === 0 ? (
        <p>Waiting for data...</p>
      ) : (
        <>
          {/* Table */}
          <table class="vitals-table" style={{ margin: '0 auto' }}>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>SpO₂ (%)</th>
                <th>Pulse (BPM)</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, idx) => (
                <tr key={idx}>
                  <td>{new Date(row.timestamp * 1000).toLocaleTimeString()}</td>
                  <td>{row.spo2}</td>
                  <td>{row.pulse}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* SpO2 Graph */}
          <div class="vitals-graph">
            <h3>SpO₂ (%)</h3>
            <ResponsiveContainer>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(t) =>
                    new Date(t * 1000).toLocaleTimeString()
                  }
                  label={{ value: "Time", position: "insideBottom", offset: -5 }}
                />
                <YAxis domain={[85, 100]} />
                <Tooltip
                  labelFormatter={(t) =>
                    new Date(t * 1000).toLocaleTimeString()
                  }
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="spo2"
                  stroke="#8884d8"
                  name="SpO₂"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Pulse Graph */}
          <div class="vitals-graph">
            <h3>Pulse (BPM)</h3>
            <ResponsiveContainer>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(t) =>
                    new Date(t * 1000).toLocaleTimeString()
                  }
                  label={{ value: "Time", position: "insideBottom", offset: -5 }}
                />
                <YAxis />
                <Tooltip
                  labelFormatter={(t) =>
                    new Date(t * 1000).toLocaleTimeString()
                  }
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="pulse"
                  stroke="#82ca9d"
                  name="Pulse"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
      <button onClick={() => navigate('/')}>Go Back Home</button>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/data/:sessionKey" element={<DataPage />} />
    </Routes>
  );
}

export default App;
