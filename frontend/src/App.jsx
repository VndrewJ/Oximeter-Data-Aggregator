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

  return (
    <div className="home-container">
      <h1>Welcome to the IoT Oximeter Project</h1>
      <p>This is the home page of your application.</p>
      <button onClick={() => navigate('/data')}>Go To Data</button>
    </div>
  );
}

function DataPage() {
  const navigate = useNavigate();
  const [data, setData] = useState([]);
  const [error, setError] = useState(false);

  // helper: ensure consistent formatting
  const formatBuffer = (buffer) =>
    buffer.map((row, i) => ({
      timestamp: Number(row["timestamp"]),
      spo2: Number(row["spo2"]),
      pulse: Number(row["pulse"]),
      idx: i
    }));

  useEffect(() => {
    // 1. Fetch initial buffer from REST API
    fetch("http://localhost:5000/data")
      .then((res) => res.json())
      .then((json) => setData(formatBuffer(json)))
      .catch(() => setError(true));

    // 2. Subscribe to websocket events
    socket.on("vitals", (buffer) => {
      setData(formatBuffer(buffer));
      setError(false);
    });

    socket.on("connect_error", () => {
      setError(true);
    });

    // cleanup
    return () => {
      socket.off("vitals");
      socket.off("connect_error");
    };
  }, []);

  const recentData = [...data].reverse();
  const tableData = recentData.slice(0, 20); // show last 20 entries in table

  return (
    <div>
      <h2>Current Oximeter Data</h2>
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
      <Route path="/data" element={<DataPage />} />
    </Routes>
  );
}

export default App;
