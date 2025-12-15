import React, { useState, useEffect } from 'react';
import './App.css';
import DemoList from './components/DemoList';
import DemoExecutor from './components/DemoExecutor';
import JobStatus from './components/JobStatus';
import { getDemos } from './services/api';

function App() {
  const [demos, setDemos] = useState([]);
  const [selectedDemo, setSelectedDemo] = useState(null);
  const [currentJob, setCurrentJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDemos();
  }, []);

  const loadDemos = async () => {
    try {
      setLoading(true);
      const data = await getDemos();
      setDemos(data);
      setError(null);
    } catch (err) {
      setError('Failed to load demos: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSelect = (demo) => {
    setSelectedDemo(demo);
    setCurrentJob(null);
  };

  const handleJobCreated = (job) => {
    setCurrentJob(job);
  };

  const handleBack = () => {
    setSelectedDemo(null);
    setCurrentJob(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🌐 Networking Demo Platform</h1>
        <p>Production-grade networking demonstrations in isolated containers</p>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-banner">
            {error}
            <button onClick={loadDemos}>Retry</button>
          </div>
        )}

        {loading ? (
          <div className="loading">Loading demos...</div>
        ) : currentJob ? (
          <div>
            <button onClick={handleBack} className="back-button">
              ← Back to Demos
            </button>
            <JobStatus jobId={currentJob.job_id} demoId={currentJob.demo_id} />
          </div>
        ) : selectedDemo ? (
          <div>
            <button onClick={handleBack} className="back-button">
              ← Back to Demos
            </button>
            <DemoExecutor demo={selectedDemo} onJobCreated={handleJobCreated} />
          </div>
        ) : (
          <DemoList demos={demos} onSelect={handleDemoSelect} />
        )}
      </main>

      <footer className="App-footer">
        <p>Secure, isolated demo execution with Docker containers</p>
      </footer>
    </div>
  );
}

export default App;
