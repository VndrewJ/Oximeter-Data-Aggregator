import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import './App.css'

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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false); // Add error state

  useEffect(() => {
    fetch('http://localhost:5000/data')
      .then(res => {
        if (!res.ok) throw new Error('Network response was not ok');
        return res.json();
      })
      .then(json => {
        setData(json);
        setLoading(false);
      })
      .catch(() => {
        setError(true); // Set error if fetch fails
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h2>Current Oximeter Data</h2>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p style={{ color: 'red' }}>Error getting data. Please try again later.</p>
      ) : (
        <table style={{ margin: '0 auto' }}>
          <thead>
            <tr>
              {data[0] && Object.keys(data[0]).map(key => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                {Object.values(row).map((val, i) => (
                  <td key={i}>{val}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
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

export default App
